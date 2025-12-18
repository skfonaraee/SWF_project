import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import openai
import psycopg2
from psycopg2.extras import RealDictCursor

# -----------------------------
# Настройки бота и ИИ
# -----------------------------
with open("app/tgbot_token.txt", "r", encoding="utf-8") as f:
    TOKEN = f.read().strip()
    
with open("app/data/openrouter.txt", "r", encoding="utf-8") as f:
    openrouter_key = f.read().strip()

openai.api_key = openrouter_key
bot = telebot.TeleBot(TOKEN)

# -----------------------------
# Подключение к PostgreSQL
# -----------------------------
conn = psycopg2.connect(
    host="localhost",
    port="5433",
    database="bot_db",
    user="postgres",
    password="1234"
)

def db_select(query, params=None):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params or ())
        return cur.fetchall()

def db_execute(query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params or ())
        conn.commit()

# -----------------------------
# Словари для сессии
# -----------------------------
user_states = {}        # chat_id → текущее состояние ИИ
expanded_sections_uni = {}  # chat_id -> {"uni_name": str, "expanded": set()}
user_navigation = {}    # chat_id -> список предыдущих состояний для кнопки "Назад"

# -----------------------------
# Направления
# -----------------------------
DIRECTIONS = {
    "business": "Бизнес / Финансы",
    "it": "IT / Инженерия / Наука", 
    "medicine": "Медицина / Биология / Здоровье",
    "art": "Искусство / Дизайн / Медиа"
}

def get_direction_keywords(direction_key):
    keywords_map = {
        "business": ["бизнес", "финанс", "менеджмент", "экономик", "маркетинг", "предпринимательство", "business", "finance", "management", "economics"],
        "it": ["информацион", "компьютер", "программир", "it", "инженер", "техническ", "наука", "технолог", "computer", "engineering", "technology", "science"],
        "medicine": ["медицин", "биолог", "здоровь", "фармацевт", "хирург", "врач", "анатом", "medicine", "biology", "health", "medical"],
        "art": ["искусств", "дизайн", "медиа", "арт", "творчеств", "худож", "музык", "кино", "art", "design", "media", "creative"]
    }
    return keywords_map.get(direction_key, [])

# -----------------------------
# Функции навигации
# -----------------------------
def add_navigation(chat_id, state):
    user = db_select("SELECT id FROM users WHERE chat_id=%s", (chat_id,))
    if user:
        user_id = user[0]['id']
        db_execute("INSERT INTO user_navigation(user_id, state) VALUES (%s, %s)", (user_id, state))
    if chat_id not in user_navigation:
        user_navigation[chat_id] = []
    user_navigation[chat_id].append(state)

def get_previous_state(chat_id):
    if chat_id in user_navigation and user_navigation[chat_id]:
        return user_navigation[chat_id].pop()
    return None

# -----------------------------
# Главное меню
# -----------------------------
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 Категория", "💬 ИИ-помощник", "🗂 Справочник")
    return markup

def reference_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Направления", callback_data="ref_directions"))
    markup.add(InlineKeyboardButton("Страны", callback_data="ref_countries"))
    markup.add(InlineKeyboardButton("Университеты", callback_data="ref_universities"))
    markup.add(InlineKeyboardButton("Гранты", callback_data="ref_grants"))
    markup.add(InlineKeyboardButton("Документы и дедлайны", callback_data="ref_documents"))
    return markup

# -----------------------------
# Функция ИИ
# -----------------------------
def ask_ai(prompt, role_context=""):
    try:
        system_prompt = """Ты консультант по поступлению и профориентации. Помогай пользователям с вопросами о поступлении в университеты, выборе направлений, подготовке документов, поиске грантов и стипендий. Отвечай подробно и поддерживающе."""
        if role_context:
            system_prompt += f"\n\nПользователь: {role_context}"
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"❗ Ошибка при обращении к ИИ: {str(e)}"

# -----------------------------
# START — выбор роли
# -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_navigation[chat_id] = []
    bot.send_message(
        chat_id,
        "Привет! 👋\nЯ — *Study Without Fear*, твой помощник в поиске университетов и стипендий за границей.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Школьник", callback_data="role_school"))
    markup.add(InlineKeyboardButton("Студент колледжа", callback_data="role_student"))
    markup.add(InlineKeyboardButton("Gap Year", callback_data="role_gap"))
    bot.send_message(chat_id, "Выберите вашу категорию:", reply_markup=markup)

# -----------------------------
# Обработка выбора роли
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def role_selected(call):
    chat_id = call.message.chat.id
    role_key = call.data.split("_")[1]
    role_map = {"school": "Школьник", "student": "Студент колледжа", "gap": "Gap Year"}
    role_name = role_map.get(role_key, role_key)

    # Сохраняем в базу
    existing_user = db_select("SELECT id FROM users WHERE chat_id=%s", (chat_id,))
    if existing_user:
        db_execute("UPDATE users SET role=%s WHERE chat_id=%s", (role_name, chat_id))
        user_id = existing_user[0]['id']
    else:
        db_execute("INSERT INTO users(chat_id, role) VALUES (%s, %s)", (chat_id, role_name))
        user_id = db_select("SELECT id FROM users WHERE chat_id=%s", (chat_id,))[0]['id']

    add_navigation(chat_id, "role_selection")

    # Выбор направления
    markup = InlineKeyboardMarkup()
    for key, direction in DIRECTIONS.items():
        markup.add(InlineKeyboardButton(direction, callback_data=f"direction_{key}"))
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_main"))

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"Ты выбрал категорию «{role_name}».\nВыбери направление:",
        reply_markup=markup
    )

# -----------------------------
# Выбор направления
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("direction_"))
def direction_selected(call):
    chat_id = call.message.chat.id
    direction_key = call.data.replace("direction_", "")
    direction_name = DIRECTIONS.get(direction_key, direction_key)

    # Сохраняем в базу
    db_execute("UPDATE users SET direction=%s WHERE chat_id=%s", (direction_name, chat_id))
    add_navigation(chat_id, "direction_selection")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать страну", callback_data="choose_country"))
    markup.add(InlineKeyboardButton("Показать университеты по направлению", callback_data=f"show_unis_by_direction_{direction_key}"))
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_roles"))

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"Вы выбрали направление: {direction_name}\nТеперь выберите страну или университет:",
        reply_markup=markup
    )

# -----------------------------
# Получение университетов по направлению
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("show_unis_by_direction_"))
def show_universities_by_direction(call):
    chat_id = call.message.chat.id
    direction_key = call.data.replace("show_unis_by_direction_", "")
    keywords = get_direction_keywords(direction_key)
    if not keywords:
        bot.send_message(chat_id, "Ключевые слова для направления не найдены.")
        return

    # SQL: поиск университетов по программам/карточке
    placeholders = ','.join(['%s']*len(keywords))
    sql_clauses = " OR ".join([f"programs ILIKE %s OR card ILIKE %s" for _ in keywords])
    sql_query = f"SELECT * FROM universities WHERE {sql_clauses}"
    params = [f"%{k}%" for k in keywords for _ in range(2)]
    universities = db_select(sql_query, params)

    if not universities:
        bot.send_message(chat_id, f"Университеты по направлению '{DIRECTIONS.get(direction_key)}' не найдены.")
        return

    text = f"🏛️ Университеты по направлению '{DIRECTIONS.get(direction_key)}':\n\n"
    markup = InlineKeyboardMarkup()
    for uni in universities[:10]:
        text += f"{uni['name']} ({uni['country']})\n"
        markup.add(InlineKeyboardButton(f"{uni['name']} ({uni['country']})", callback_data=f"uni_{uni['id']}"))

    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_direction"))

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

# -----------------------------
# Показ информации о университете
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("uni_"))
def uni_selected(call):
    chat_id = call.message.chat.id
    uni_id = int(call.data.replace("uni_", ""))
    uni = db_select("SELECT * FROM universities WHERE id=%s", (uni_id,))
    if not uni:
        bot.send_message(chat_id, "Информация о университете не найдена.")
        return
    uni = uni[0]

    text = uni['card'] or "Информация недоступна"
    markup = InlineKeyboardMarkup()
    for section in ["documents", "scholarships", "deadlines", "process", "programs"]:
        if uni.get(section):
            markup.add(InlineKeyboardButton(section.capitalize(), callback_data=f"uni_section_{section}_{uni_id}"))

    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_direction"))
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

# -----------------------------
# Запуск бота
# -----------------------------
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
