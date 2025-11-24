import json
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import openai
from functools import partial


# -----------------------------
# Чтение токена
# -----------------------------
with open("app/tgbot_token.txt", "r", encoding="utf-8") as f:
    TOKEN = f.read().strip()
    
with open("app/data/openrouter.txt", "r", encoding="utf-8") as f:
    openrouter_key = f.read().strip()

openai.api_key = openrouter_key

bot = telebot.TeleBot(TOKEN)

# -----------------------------
# Глобальные словари
# -----------------------------
user_roles = {}         # chat_id → роль
user_countries = {}     # chat_id → страна
user_directions = {}    # chat_id → направление
user_states = {}        # chat_id → текущее состояние (для ИИ и т.д.)
expanded_sections_uni = {}  # chat_id -> {"uni_name": str, "expanded": set()}
user_navigation = {}    # chat_id -> список предыдущих состояний для кнопки "Назад"

# -----------------------------
# Чтение данных из JSON
# -----------------------------
with open("universities.json", "r", encoding="utf-8") as f:
    university_data = json.load(f)

# Направления для выбора
DIRECTIONS = {
    "business": "Бизнес / Финансы",
    "it": "IT / Инженерия / Наука", 
    "medicine": "Медицина / Биология / Здоровье",
    "art": "Искусство / Дизайн / Медиа"
}

# -----------------------------
# Функция для общения с ИИ
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
# Навигационные функции
# -----------------------------
def add_navigation(chat_id, state):
    """Добавляет состояние в историю навигации"""
    if chat_id not in user_navigation:
        user_navigation[chat_id] = []
    user_navigation[chat_id].append(state)

def get_previous_state(chat_id):
    """Возвращает предыдущее состояние и удаляет его из истории"""
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
# START — выбор роли
# -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # Очищаем историю навигации
    if chat_id in user_navigation:
        user_navigation[chat_id] = []
    
    bot.send_message(
        chat_id,
        "Привет! 👋\n"
        "Я — *Study Without Fear*, твой помощник в поиске университетов и стипендий за границей.\n\n"
        "С моей помощью ты можешь:\n"
        "— Найти подходящие университеты по стране и направлению 🎓\n"
        "— Узнать актуальные гранты и стипендии 💰\n"
        "— Узнать дедлайны и требования для поступления 📅\n\n"
        "Выбери категорию ниже, чтобы начать!",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )
    
    # Сразу показываем выбор категории
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Школьник", callback_data="role_school"))
    markup.add(InlineKeyboardButton("Студент колледжа", callback_data="role_student"))
    markup.add(InlineKeyboardButton("Gap Year", callback_data="role_gap"))
    bot.send_message(chat_id, "👇 Выберите вашу категорию:", reply_markup=markup)

# -----------------------------
# Обработка текстовых сообщений (главное меню)
# -----------------------------
@bot.message_handler(func=lambda message: message.text in ["📚 Категория", "💬 ИИ-помощник", "🗂 Справочник"])
def handle_main_menu(message):
    chat_id = message.chat.id
    
    if message.text == "📚 Категория":
        add_navigation(chat_id, "main_menu")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Школьник", callback_data="role_school"))
        markup.add(InlineKeyboardButton("Студент колледжа", callback_data="role_student"))
        markup.add(InlineKeyboardButton("Gap Year", callback_data="role_gap"))
        bot.send_message(chat_id, "👇 Выберите вашу категорию:", reply_markup=markup)
        
    elif message.text == "💬 ИИ-помощник":
        user_states[chat_id] = "ai_assistant"
        role = user_roles.get(chat_id, "пользователь")
        bot.send_message(
            chat_id, 
            f"🤖 Режим ИИ-помощника\n\n"
            f"Я здесь, чтобы помочь с вопросами о поступлении, выборе направления, "
            f"подготовке документов и поиске грантов.\n\n"
            f"Задайте ваш вопрос:",
            reply_markup=main_menu()
        )
        
    elif message.text == "🗂 Справочник":
        add_navigation(chat_id, "main_menu")
        bot.send_message(
            chat_id,
            "📚 Справочник:\n\n"
            "Здесь вы можете найти информацию по различным аспектам поступления:",
            reply_markup=reference_menu()
        )

# -----------------------------
# Обработка сообщений в режиме ИИ
# -----------------------------
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "ai_assistant")
def handle_ai_message(message):
    chat_id = message.chat.id
    role = user_roles.get(chat_id, "пользователь")
    
    bot.send_message(chat_id, "🤔 Думаю над ответом...")
    
    response = ask_ai(message.text, f"Категория пользователя: {role}")
    
    bot.send_message(chat_id, f"💡 {response}")

# -----------------------------
# Выбор роли
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def role_selected(call):
    role_map = {
        "school": "Школьник",
        "student": "Студент колледжа", 
        "gap": "Gap Year"
    }
    
    role_key = call.data.split("_")[1]
    role_name = role_map.get(role_key, role_key)
    chat_id = call.message.chat.id
    user_roles[chat_id] = role_name
    
    # Сбрасываем состояние ИИ
    if chat_id in user_states:
        del user_states[chat_id]
    
    # Добавляем в навигацию
    add_navigation(chat_id, "role_selection")
    
    # Предлагаем выбрать направление
    markup = InlineKeyboardMarkup()
    for key, direction in DIRECTIONS.items():
        markup.add(InlineKeyboardButton(direction, callback_data=f"direction_{key}"))
    
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_main"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"Ты выбрал категорию «{role_name}».\n\n"
             f"🎓 Я могу помочь тебе:\n\n"
             f"• Найти университеты и программы для поступления\n"
             f"• Узнать доступные гранты и стипендии\n"  
             f"• Проверить дедлайны подачи\n"
             f"• Посмотреть список необходимых документов\n"
             f"• Получить рекомендации с помощью ИИ\n\n"
             f"Выбери направление, чтобы продолжить:",
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
    user_directions[chat_id] = direction_name
    
    # Добавляем в навигацию
    add_navigation(chat_id, "direction_selection")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать страну", callback_data="choose_country"))
    markup.add(InlineKeyboardButton("Показать университеты по направлению", callback_data=f"show_unis_by_direction_{direction_key}"))
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_roles"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"🎯 Вы выбрали направление: {direction_name}\n\n"
             f"Теперь вы можете выбрать страну или сразу посмотреть университеты по этому направлению:",
        reply_markup=markup
    )

# -----------------------------
# Показать университеты по направлению
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("show_unis_by_direction_"))
def show_universities_by_direction(call):
    chat_id = call.message.chat.id
    direction_key = call.data.replace("show_unis_by_direction_", "")
    direction_name = DIRECTIONS.get(direction_key, direction_key)
    
    # Добавляем в навигацию
    add_navigation(chat_id, "universities_by_direction")
    
    # Поиск университетов по направлению
    found_universities = []
    
    for country, universities in university_data.items():
        for uni_name, uni_info in universities.items():
            # Проверяем программы университета на соответствие направлению
            programs = uni_info.get("programs", "").lower()
            card = uni_info.get("card", "").lower()
            
            # Ищем ключевые слова в программах и карточке университета
            if any(keyword in programs or keyword in card for keyword in get_direction_keywords(direction_key)):
                found_universities.append((country, uni_name, uni_info))
    
    if not found_universities:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_direction"))
        bot.send_message(
            chat_id,
            f"😔 По направлению '{direction_name}' университеты не найдены.\n"
            f"Попробуйте выбрать другую страну или направление.",
            reply_markup=markup
        )
        return
    
    # Отправляем список университетов
    text = f"🏛️ Университеты по направлению '{direction_name}':\n\n"
    
    for i, (country, uni_name, uni_info) in enumerate(found_universities[:10], 1):  # Ограничиваем 10 университетами
        text += f"{i}. {uni_name} ({country})\n"
    
    if len(found_universities) > 10:
        text += f"\n... и еще {len(found_universities) - 10} университетов"
    
    # Кнопки для выбора конкретного университета
    markup = InlineKeyboardMarkup()
    for country, uni_name, uni_info in found_universities[:5]:  # Ограничиваем 5 кнопками
        markup.add(InlineKeyboardButton(
            f"{uni_name} ({country})", 
            callback_data=f"uni_{country}_{uni_name}"
        ))
    
    markup.add(InlineKeyboardButton("Выбрать страну", callback_data="choose_country"))
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_direction"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text, 
        reply_markup=markup
    )

def get_direction_keywords(direction_key):
    """Возвращает ключевые слова для поиска по направлениям"""
    keywords_map = {
        "business": ["бизнес", "финанс", "менеджмент", "экономик", "маркетинг", "предпринимательство", "business", "finance", "management", "economics"],
        "it": ["информацион", "компьютер", "программир", "it", "инженер", "техническ", "наука", "технолог", "computer", "engineering", "technology", "science"],
        "medicine": ["медицин", "биолог", "здоровь", "фармацевт", "хирург", "врач", "анатом", "medicine", "biology", "health", "medical"],
        "art": ["искусств", "дизайн", "медиа", "арт", "творчеств", "худож", "музык", "кино", "art", "design", "media", "creative"]
    }
    return keywords_map.get(direction_key, [])

# -----------------------------
# Выбор страны
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data == "choose_country")
def choose_country(call):
    chat_id = call.message.chat.id
    add_navigation(chat_id, "country_selection")
    
    markup = InlineKeyboardMarkup()
    countries = list(university_data.keys())
    for c in countries:
        markup.add(InlineKeyboardButton(c, callback_data=f"country_{c}"))
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_direction"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="Выберите страну:",
        reply_markup=markup
    )

# -----------------------------
# Выбор университета по стране
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def country_selected(call):
    chat_id = call.message.chat.id
    country = call.data.replace("country_", "")
    user_countries[chat_id] = country

    universities = university_data.get(country, {})
    if not universities:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_countries"))
        bot.send_message(chat_id, "Университеты для этой страны пока не добавлены.", reply_markup=markup)
        return

    add_navigation(chat_id, "universities_list")

    markup = InlineKeyboardMarkup()
    for uni_name in universities.keys():
        markup.add(InlineKeyboardButton(uni_name, callback_data=f"uni_{country}_{uni_name}"))
    markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_countries"))
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"Выберите университет в {country}:", 
        reply_markup=markup
    )

# -----------------------------
# Показ card университета + кнопки
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("uni_"))
def uni_selected(call):
    chat_id = call.message.chat.id
    parts = call.data.split("_")
    if len(parts) >= 3:
        country = parts[1]
        uni_name = "_".join(parts[2:])
    else:
        bot.send_message(chat_id, "Ошибка при выборе университета")
        return
        
    if country not in university_data or uni_name not in university_data[country]:
        bot.send_message(chat_id, "Информация об университете не найдена")
        return
        
    uni_info = university_data[country][uni_name]

    expanded_sections_uni[chat_id] = {"uni_name": uni_name, "expanded": set()}
    add_navigation(chat_id, "university_view")

    text = uni_info.get("card", "Информация о университете недоступна")
    markup = InlineKeyboardMarkup()

    # кнопки раскрытия разделов
    for section in ["documents", "scholarships", "deadlines", "process", "programs"]:
        if section in uni_info:
            markup.add(InlineKeyboardButton(section.capitalize(), callback_data=f"uni_section_{section}"))

    # кнопки ссылок
    links = uni_info.get("links", {})
    for name, url in links.items():
        markup.add(InlineKeyboardButton(name.capitalize(), url=url))

    # кнопка возврата
    markup.add(InlineKeyboardButton("← Назад к университету", callback_data=f"back_to_university_{country}"))

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text, 
        reply_markup=markup
    )

# -----------------------------
# Раскрытие секций университета
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("uni_section_"))
def uni_section_toggle(call):
    chat_id = call.message.chat.id
    section = call.data.replace("uni_section_", "")

    if chat_id not in expanded_sections_uni:
        return

    uni_name = expanded_sections_uni[chat_id]["uni_name"]

    # находим страну
    country = None
    for c, unis in university_data.items():
        if uni_name in unis:
            country = c
            break
    if not country:
        return

    uni_info = university_data[country][uni_name]

    # Тоггл секции: если открыта — закрыть, если закрыта — открыть
    if section in expanded_sections_uni[chat_id]["expanded"]:
        expanded_sections_uni[chat_id]["expanded"].remove(section)
    else:
        expanded_sections_uni[chat_id]["expanded"].add(section)

    # Формируем текст
    text = uni_info.get("card", "")
    for sec in ["documents", "scholarships", "deadlines", "process", "programs"]:
        if sec in expanded_sections_uni[chat_id]["expanded"] and sec in uni_info:
            text += f"\n\n*{sec.capitalize()}:*\n{uni_info[sec]}"

    # Формируем кнопки
    markup = InlineKeyboardMarkup()
    for sec in ["documents", "scholarships", "deadlines", "process", "programs"]:
        if sec in uni_info:
            if sec in expanded_sections_uni[chat_id]["expanded"]:
                btn_text = f"✅ {sec.capitalize()}"  # отмечаем, что секция открыта
            else:
                btn_text = sec.capitalize()
            markup.add(InlineKeyboardButton(btn_text, callback_data=f"uni_section_{sec}"))

    links = uni_info.get("links", {})
    for name, url in links.items():
        markup.add(InlineKeyboardButton(name.capitalize(), url=url))

    # кнопка возврата
    markup.add(InlineKeyboardButton("← Назад к университету", callback_data=f"back_to_university_{country}"))

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=text, 
        parse_mode="Markdown", 
        reply_markup=markup
    )

# -----------------------------
# Обработка кнопки "Назад"
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("back_"))
def handle_back(call):
    chat_id = call.message.chat.id
    back_action = call.data
    
    if back_action == "back_to_main":
        # Возврат в главное меню
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="Главное меню",
            reply_markup=main_menu()
        )
        
    elif back_action == "back_to_roles":
        # Возврат к выбору роли
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Школьник", callback_data="role_school"))
        markup.add(InlineKeyboardButton("Студент колледжа", callback_data="role_student"))
        markup.add(InlineKeyboardButton("Gap Year", callback_data="role_gap"))
        markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_main"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="👇 Выберите вашу категорию:",
            reply_markup=markup
        )
        
    elif back_action == "back_to_direction":
        # Возврат к выбору направления
        role_name = user_roles.get(chat_id, "пользователь")
        markup = InlineKeyboardMarkup()
        for key, direction in DIRECTIONS.items():
            markup.add(InlineKeyboardButton(direction, callback_data=f"direction_{key}"))
        markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_roles"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"Ты выбрал категорию «{role_name}».\n\nВыбери направление, чтобы продолжить:",
            reply_markup=markup
        )
        
    elif back_action == "back_to_countries":
        # Возврат к выбору страны
        markup = InlineKeyboardMarkup()
        countries = list(university_data.keys())
        for c in countries:
            markup.add(InlineKeyboardButton(c, callback_data=f"country_{c}"))
        markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_direction"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="Выберите страну:",
            reply_markup=markup
        )
        
    elif back_action.startswith("back_to_university_"):
        # Возврат к просмотру университета
        country = back_action.replace("back_to_university_", "")
        if chat_id in user_countries:
            user_countries[chat_id] = country
            
        # Повторно показываем список университетов страны
        universities = university_data.get(country, {})
        markup = InlineKeyboardMarkup()
        for uni_name in universities.keys():
            markup.add(InlineKeyboardButton(uni_name, callback_data=f"uni_{country}_{uni_name}"))
        markup.add(InlineKeyboardButton("← Назад", callback_data="back_to_countries"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"Выберите университет в {country}:", 
            reply_markup=markup
        )

# -----------------------------
# Обработка справочника
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("ref_"))
def handle_reference(call):
    chat_id = call.message.chat.id
    ref_type = call.data.replace("ref_", "")
    
    ref_texts = {
        "directions": "🎯 Направления:\n\n• Бизнес / Финансы\n• IT / Инженерия / Наука\n• Медицина / Биология / Здоровье\n• Искусство / Дизайн / Медиа",
        "countries": "🌍 Страны:\n\nДоступные для поступления страны с университетами в нашей базе данных.",
        "universities": "🏛️ Университеты:\n\nИнформация о различных университетах, их программах и требованиях.",
        "grants": "💰 Гранты:\n\nИнформация о доступных стипендиях и грантах для международных студентов.",
        "documents": "📄 Документы и дедлайны:\n\nСписок необходимых документов и сроки подачи заявок."
    }
    
    text = ref_texts.get(ref_type, "Информация не найдена")
    bot.send_message(chat_id, text, reply_markup=reference_menu())

# -----------------------------
# Запуск бота
# -----------------------------
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()