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
expanded_sections_uni = {}  # chat_id -> {"uni_name": str, "expanded": set()}

# -----------------------------
# Чтение данных из JSON
# -----------------------------
with open("universities.json", "r", encoding="utf-8") as f:
    university_data = json.load(f)


# Функция для общения с ИИ
def ask_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"❗ Ошибка: {str(e)}"


# -----------------------------
# START — выбор роли
# -----------------------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! 👋\n"
        "Я — *Study Without Fear*, твой помощник в поиске университетов и стипендий за границей.\n\n"
        "С моей помощью ты можешь:\n"
        "— Найти подходящие университеты по стране и направлению 🎓\n"
        "— Узнать актуальные гранты и стипендии 💰\n"
        "— Узнать дедлайны и требования для поступления 📅\n\n"
        "Выбери категорию ниже, чтобы начать!",
        parse_mode="Markdown"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Школьник", callback_data="role_school"))
    markup.add(types.InlineKeyboardButton("Студент колледжа", callback_data="role_student"))
    markup.add(types.InlineKeyboardButton("Gap Year", callback_data="role_gap"))
    bot.send_message(message.chat.id, "👇 Выберите вашу категорию:", reply_markup=markup)

# -----------------------------
# Выбор роли
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def role_selected(call):
    role = call.data.split("_")[1]
    chat_id = call.message.chat.id
    user_roles[chat_id] = role

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Выбрать страну", callback_data="choose_country"))
    bot.send_message(chat_id, f"Вы выбрали категорию «{role}».\nТеперь выберите страну:", reply_markup=markup)

# -----------------------------
# Выбор страны
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data == "choose_country")
def choose_country(call):
    markup = types.InlineKeyboardMarkup()
    countries = list(university_data.keys())
    for c in countries:
        markup.add(types.InlineKeyboardButton(c, callback_data=f"country_{c}"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите страну:",
                          reply_markup=markup)

# -----------------------------
# Выбор университета
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def country_selected(call):
    chat_id = call.message.chat.id
    country = call.data.replace("country_", "")
    user_countries[chat_id] = country

    universities = university_data.get(country, {})
    if not universities:
        bot.send_message(chat_id, "Университеты для этой страны пока не добавлены.")
        return

    markup = types.InlineKeyboardMarkup()
    for uni_name in universities.keys():
        markup.add(types.InlineKeyboardButton(uni_name, callback_data=f"uni_{country}_{uni_name}"))
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=f"Выберите университет в {country}:", reply_markup=markup)

# -----------------------------
# Показ card университета + кнопки
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("uni_"))
def uni_selected(call):
    chat_id = call.message.chat.id
    _, country, uni_name = call.data.split("_", 2)
    uni_info = university_data[country][uni_name]

    expanded_sections_uni[chat_id] = {"uni_name": uni_name, "expanded": set()}

    text = uni_info.get("card", "Информация о университете недоступна")
    markup = types.InlineKeyboardMarkup()

    # кнопки раскрытия разделов
    for section in ["documents", "scholarships", "deadlines", "process", "programs"]:
        if section in uni_info:
            markup.add(types.InlineKeyboardButton(section.capitalize(), callback_data=f"uni_section_{section}"))

    # кнопки ссылок
    links = uni_info.get("links", {})
    for name, url in links.items():
        markup.add(types.InlineKeyboardButton(name.capitalize(), url=url))

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=text, reply_markup=markup)
# -----------------------------
# Раскрытие секций
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
    markup = types.InlineKeyboardMarkup()
    for sec in ["documents", "scholarships", "deadlines", "process", "programs"]:
        if sec in uni_info:
            if sec in expanded_sections_uni[chat_id]["expanded"]:
                btn_text = f"✅ {sec.capitalize()}"  # отмечаем, что секция открыта
            else:
                btn_text = sec.capitalize()
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"uni_section_{sec}"))

    links = uni_info.get("links", {})
    for name, url in links.items():
        markup.add(types.InlineKeyboardButton(name.capitalize(), url=url))

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=text, parse_mode="Markdown", reply_markup=markup)
# -----------------------------
# Запуск бота
# -----------------------------
bot.infinity_polling()
