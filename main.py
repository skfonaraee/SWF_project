import telebot
from telebot import types

# -----------------------------
# Чтение токена из файла
# -----------------------------
with open("app/tgbot_token.txt", "r", encoding="utf-8") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)

# -----------------------------
# Глобальные словари для ролей, стран и раскрытых секций
# -----------------------------
expanded_sections = {}  # chat_id → раскрытые секции
user_roles = {}         # chat_id → роль
user_countries = {}     # chat_id → выбранная страна

# -----------------------------
# Тексты документов по стране и роли
# -----------------------------
docs_data = {
    "Венгрия": {
        "school": {
            "Академические": "Аттестат / диплом предыдущего уровня\nТабель / GPA\nПеревод на английский или венгерский + нотариальное заверение",
            "Личность": "Паспорт / ID\nФото (паспортного формата)",
            "Языковые": "Сертификат английского языка (IELTS/TOEFL)\nДля венгерских программ: знание венгерского (по необходимости)",
            "Для гранта": "Мотивационное письмо\n1–2 рекомендательных письма\nПлан обучения / Study Plan (по необходимости)",
            "Дополнительно": "Letter of Acceptance (если есть)\nМедицинская справка (для визы)"
        },
        "student": {
            "Академические": "Диплом предыдущего уровня (college / associate degree)\nТранскрипт / академическая справка",
            "Личность": "Паспорт / ID\nФото",
            "Языковые": "Сертификат английского языка (IELTS/TOEFL)",
            "Для гранта": "Мотивационное письмо для гранта\nРекомендательные письма",
            "Дополнительно": "CV / портфолио (если есть)\nВыписка родителей (для визы, если студент <18)\nНотариальный перевод всех документов"
        },
        "gap": {
            "Академические": "Аттестат / транскрипт\nПеревод всех документов",
            "Личность": "Паспорт",
            "Языковые": "Сертификат уровня языка (если есть)",
            "Для гранта": "Мотивационное письмо\nCV\nВыписка с банковского счёта родителей (если требуется)",
            "Дополнительно": "Прочие документы по требованию учебного заведения"
        }
    },
    "Германия": {
        "school": {
            "Академические": "Аттестат / диплом\nПеревод на английский / немецкий + нотариальное заверение",
            "Личность": "Паспорт / ID",
            "Языковые": "Сертификат английского или немецкого языка",
            "Для гранта": "Мотивационное письмо\nРекомендательные письма",
            "Дополнительно": "CV / Letter of Acceptance (если есть)"
        },
        "student": {
            "Академические": "Диплом college / bachelor\nТранскрипт академической успеваемости\nПеревод на немецкий/английский",
            "Личность": "Паспорт / ID",
            "Языковые": "Сертификат уровня языка (IELTS / TestDaF / DSH)",
            "Для гранта": "Мотивационное письмо\nРекомендательные письма",
            "Дополнительно": "CV / Letter of Acceptance"
        },
        "gap": {
            "Академические": "Аттестат / транскрипт\nПеревод всех документов",
            "Личность": "Паспорт",
            "Языковые": "Сертификат языка (если есть)",
            "Для гранта": "Мотивационное письмо\nCV",
            "Дополнительно": "Прочие документы по требованию учебного заведения"
        }
    },
    "Южная Корея": {
        "school": {
            "Академические": "Аттестат / диплом\nПеревод на английский + нотариальное заверение",
            "Личность": "Паспорт / ID",
            "Языковые": "Сертификат английского языка\nДля корейских программ: TOPIK",
            "Для гранта": "Мотивационное письмо\nРекомендательные письма",
            "Дополнительно": "Letter of Acceptance (если есть)"
        },
        "student": {
            "Академические": "Диплом предыдущего уровня\nТранскрипт / академическая справка",
            "Личность": "Паспорт / ID",
            "Языковые": "Сертификат английского / корейского языка",
            "Для гранта": "Мотивационное письмо\nРекомендательные письма",
            "Дополнительно": "CV / портфолио"
        },
        "gap": {
            "Академические": "Аттестат / транскрипт\nПеревод документов",
            "Личность": "Паспорт",
            "Языковые": "Сертификат языка (если есть)",
            "Для гранта": "Мотивационное письмо\nCV",
            "Дополнительно": "Прочие документы по требованию учебного заведения"
        }
    },
    "Япония": {
        "school": {
            "Академические": "Аттестат / диплом\nПеревод на английский / японский",
            "Личность": "Паспорт / ID",
            "Языковые": "Сертификат английского / японского языка",
            "Для гранта": "Мотивационное письмо\nРекомендательные письма",
            "Дополнительно": "Letter of Acceptance (если есть)"
        },
        "student": { ... },
        "gap": { ... }
    },
    "Нидерланды": {
        "school": {
            "Академические": "Аттестат / диплом\nПеревод на английский",
            "Личность": "Паспорт / ID",
            "Языковые": "Сертификат английского языка",
            "Для гранта": "Мотивационное письмо\nРекомендательные письма",
            "Дополнительно": "Letter of Acceptance (если есть)"
        },
        "student": { ... },
        "gap": { ... }
    }
}

# Университеты / гранты по странам и ролям
university_data = {
        "Венгрия": {
            "school": {
                "text": (
                    "🎓 Венгрия — школьник:\n"
                    "Топовые:\nBGE – Budapest Business University: Бизнес / Финансы\n"
                    "ELTE – Eötvös Loránd University: IT / Инженерия\n\n"
                    "Доступные:\nMETU – Metropolitan University: Искусство / Дизайн\n"
                    "University of Pécs: Медицина\n"
                    "University of Debrecen: Бизнес / Экономика\n\n"
                    "💰 Гранты:\nStipendium Hungaricum (Full)\n\n"
                    "📅 Дедлайны:\nГрант: 15 января\nУниверситеты: до 30 июня\n\n📄 Документы — через кнопку ниже"
                ),
                "links": [
                    ("BGE", "https://www.uni-bge.hu/"),
                    ("ELTE", "https://www.elte.hu/en"),
                    ("METU", "https://www.metropolitan.hu/"),
                    ("University of Pécs", "https://www.pte.hu/"),
                    ("University of Debrecen", "https://unideb.hu/")
                ]
            },
            "student": {
                "text": (
                    "🎓 Венгрия — студент колледжа:\n"
                    "Топовые:\nBGE – Budapest Business University\n"
                    "Доступные:\nMETU – Metropolitan University\n\n"
                    "💰 Гранты:\nStipendium Hungaricum (Full)\n\n"
                    "📅 Дедлайны:\nSH: 15 января\nУниверситеты: до 30 июня\n\n📄 Документы — через кнопку ниже"
                ),
                "links": [
                    ("BGE", "https://www.uni-bge.hu/"),
                    ("METU", "https://www.metropolitan.hu/")
                ]
            },
            "gap": {
                "text": (
                    "🎓 Венгрия — Gap Year:\n"
                    "Программы:\nGoethe-Institut (курс немецкого)\nStudienkolleg (подготовка к университету)\n\n"
                    "💰 Гранты:\nDAAD Preparatory Year Scholarship\n\n"
                    "📅 Дедлайны: до 15 июня\n\n📄 Документы — через кнопку ниже"
                ),
                "links": [
                    ("Goethe-Institut", "https://www.goethe.de/en/index.html"),
                    ("Studienkolleg", "https://www.studienkolleg.de/")
                ]
            }
        },
        "Германия": {
        "school": {
            "text": "🎓 Германия — школьник: топовые и доступные университеты...\n📄 Документы — через кнопку ниже",
            "links": [
                ("RWTH Aachen", "https://www.rwth-aachen.de/cms/~a/root/?lidx=1"),
                ("TUM", "https://www.tum.de/en/"),
                ("KIT", "https://www.kit.edu/english/"),
                ("University of Stuttgart", "https://www.uni-stuttgart.de/en/"),
                ("Darmstadt University", "https://www.tu-darmstadt.de/index.en.jsp"),
                ("DAAD Scholarship", "https://www.daad.de/en/studying-in-germany/scholarships/daad-scholarships/"),
                ("Deutschlandstipendium", "https://www.deutschlandstipendium.de/deutschlandstipendium/de/home/home_node.html")
            ]
        },
        "student": {
            "text": "🎓 Германия — студент колледжа: университеты для продолжения обучения...\n📄 Документы — через кнопку ниже",
            "links": [
                ("RWTH Aachen", "https://www.rwth-aachen.de/cms/~a/root/?lidx=1"),
                ("TUM", "https://www.tum.de/en/"),
                ("KIT", "https://www.kit.edu/english/"),
                ("University of Stuttgart", "https://www.uni-stuttgart.de/en/"),
                ("Darmstadt University", "https://www.tu-darmstadt.de/index.en.jsp"),
                ("DAAD Scholarship", "https://www.daad.de/en/studying-in-germany/scholarships/daad-scholarships/"),
                ("Deutschlandstipendium", "https://www.deutschlandstipendium.de/deutschlandstipendium/de/home/home_node.html")
            ]
        },
        "gap": {
            "text": "🎓 Германия — Gap Year: подготовительные программы...\n📄 Документы — через кнопку ниже",
            "links": [
                ("Goethe-Institut", "https://www.goethe.de/en/index.html"),
                ("Studienkolleg", "https://www.studienkolleg.de/"),
                ("DAAD Scholarship", "https://www.daad.de/en/studying-in-germany/scholarships/daad-scholarships/"),
                ("Deutschlandstipendium", "https://www.deutschlandstipendium.de/deutschlandstipendium/de/home/home_node.html")
            ]
        }
    },
    "Южная Корея": {
        "school": {
            "text": "🎓 Южная Корея — школьник: топовые и доступные университеты...\n📄 Документы — через кнопку ниже",
            "links": [
                ("KAIST", "https://www.kaist.ac.kr/en/"),
                ("POSTECH", "https://www.postech.ac.kr/eng/"),
                ("Seoul National University", "https://en.snu.ac.kr/"),
                ("Yonsei University", "https://www.yonsei.ac.kr/en_sc/"),
                ("Korea University", "https://www.korea.edu/"),
                ("KGSP", "https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do")
            ]
        },
        "student": {
            "text": "🎓 Южная Корея — студент колледжа: университеты для продолжения обучения...\n📄 Документы — через кнопку ниже",
            "links": [
                ("KAIST", "https://www.kaist.ac.kr/en/"),
                ("POSTECH", "https://www.postech.ac.kr/eng/"),
                ("Seoul National University", "https://en.snu.ac.kr/"),
                ("Yonsei University", "https://www.yonsei.ac.kr/en_sc/"),
                ("Korea University", "https://www.korea.edu/"),
                ("KGSP", "https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do")
            ]
        },
        "gap": {
            "text": "🎓 Южная Корея — Gap Year: подготовительные программы...\n📄 Документы — через кнопку ниже",
            "links": [
                ("Goethe-Institut", "https://www.goethe.de/en/index.html"),
                ("KGSP", "https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do")
            ]
        }
    },
    "Япония": {
        "school": {
            "text": "🎓 Япония — школьник: топовые и доступные университеты...\n📄 Документы — через кнопку ниже",
            "links": [
                ("University of Tokyo", "https://www.u-tokyo.ac.jp/en/"),
                ("Hitotsubashi University", "https://www.hit-u.ac.jp/eng/"),
                ("Ritsumeikan University", "https://en.ritsumei.ac.jp/"),
                ("Waseda University", "https://www.waseda.jp/top/en"),
                ("MEXT Scholarship", "https://www.studyinjapan.go.jp/en/smap-stopj-applications-mext.html")
            ]
        },
        "student": {
            "text": "🎓 Япония — студент колледжа: университеты для продолжения обучения...\n📄 Документы — через кнопку ниже",
            "links": [
                ("University of Tokyo", "https://www.u-tokyo.ac.jp/en/"),
                ("Hitotsubashi University", "https://www.hit-u.ac.jp/eng/"),
                ("MEXT Scholarship", "https://www.studyinjapan.go.jp/en/smap-stopj-applications-mext.html")
            ]
        },
        "gap": {
            "text": "🎓 Япония — Gap Year: подготовительные программы...\n📄 Документы — через кнопку ниже",
            "links": [
                ("Goethe-Institut", "https://www.goethe.de/en/index.html"),
                ("MEXT Scholarship", "https://www.studyinjapan.go.jp/en/smap-stopj-applications-mext.html")
            ]
        }
    },
    "Нидерланды": {
        "school": {
            "text": "🎓 Нидерланды — школьник: топовые и доступные университеты...\n📄 Документы — через кнопку ниже",
            "links": [
                ("University of Amsterdam", "https://www.uva.nl/en"),
                ("Delft University of Technology", "https://www.tudelft.nl/en/"),
                ("Erasmus University Rotterdam", "https://www.eur.nl/en"),
                ("Twente University", "https://www.utwente.nl/en"),
                ("Holland Scholarship", "https://www.studyinholland.nl/finances/holland-scholarship"),
                ("Orange Tulip Scholarship", "https://www.nesoindonesia.or.id/study-abroad/orange-tulip-scholarship")
            ]
        },
        "student": {
            "text": "🎓 Нидерланды — студент колледжа: университеты для продолжения обучения...\n📄 Документы — через кнопку ниже",
            "links": [
                ("University of Amsterdam", "https://www.uva.nl/en"),
                ("Delft University of Technology", "https://www.tudelft.nl/en/"),
                ("Holland Scholarship", "https://www.studyinholland.nl/finances/holland-scholarship"),
                ("Orange Tulip Scholarship", "https://www.nesoindonesia.or.id/study-abroad/orange-tulip-scholarship")
            ]
        },
        "gap": {
            "text": "🎓 Нидерланды — Gap Year: подготовительные программы...\n📄 Документы — через кнопку ниже",
            "links": [
                ("Goethe-Institut", "https://www.goethe.de/en/index.html"),
                ("Holland Scholarship", "https://www.studyinholland.nl/finances/holland-scholarship"),
                ("Orange Tulip Scholarship", "https://www.nesoindonesia.or.id/study-abroad/orange-tulip-scholarship")
            ]
        }
    }
}


# -----------------------------
# START — показываем приветствие и меню выбора роли
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
# Обработка выбора роли
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("role_"))
def role_selected(call):
    role = call.data.split("_")[1]
    chat_id = call.message.chat.id
    user_roles[chat_id] = role  # сохраняем роль

    text = f"Вы выбрали категорию «{role}».\nВыберите страну или направление, чтобы продолжить."
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Выбрать страну", callback_data="choose_country"))
    markup.add(types.InlineKeyboardButton("Выбрать направление", callback_data="choose_direction"))
    bot.send_message(chat_id, text, reply_markup=markup)

# -----------------------------
# Выбор страны
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data == "choose_country")
def choose_country(call):
    markup = types.InlineKeyboardMarkup()
    countries = ["Венгрия", "Германия", "Южная Корея", "Япония", "Нидерланды"]
    for c in countries:
        markup.add(types.InlineKeyboardButton(c, callback_data=f"country_{c}"))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите страну:",
                          reply_markup=markup)

# -----------------------------
# Выбор страны — показ университетов и грантов
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def country_selected(call):
    chat_id = call.message.chat.id
    country = call.data.replace("country_", "")
    user_countries[chat_id] = country
    role = user_roles.get(chat_id, "school")

    data = university_data.get(country, {}).get(role, {})
    text = data.get("text", "Информация недоступна")
    links = data.get("links", [])

    markup = types.InlineKeyboardMarkup()
    for name, url in links:
        markup.add(types.InlineKeyboardButton(name, url=url))
    markup.add(types.InlineKeyboardButton("📄 Документы", callback_data="docs"))

    bot.edit_message_text(chat_id=chat_id,
                          message_id=call.message.message_id,
                          text=text,
                          reply_markup=markup)

    # Данные по университетам
    

# -----------------------------
# Документы — аккордеон
# -----------------------------
@bot.callback_query_handler(func=lambda call: call.data == "docs")
def docs(call):
    chat_id = call.message.chat.id
    expanded_sections[chat_id] = set()
    text = "📄 Документы:\n(нажмите на раздел, чтобы развернуть)"
    markup = types.InlineKeyboardMarkup()
    sections = ["Академические", "Личность", "Языковые", "Для гранта", "Дополнительно"]
    for s in sections:
        markup.add(types.InlineKeyboardButton(s, callback_data=f"doc_toggle_{s}"))
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("doc_toggle_"))
def doc_toggle(call):
    chat_id = call.message.chat.id
    role = user_roles.get(chat_id, "school")
    country = user_countries.get(chat_id, "Венгрия")

    if chat_id not in expanded_sections:
        expanded_sections[chat_id] = set()

    section = call.data.replace("doc_toggle_", "")
    if section in expanded_sections[chat_id]:
        expanded_sections[chat_id].remove(section)
    else:
        expanded_sections[chat_id].add(section)

    text = "📄 Документы:\n"
    for sec in ["Академические", "Личность", "Языковые", "Для гранта", "Дополнительно"]:
        if sec in expanded_sections[chat_id]:
            text += f"\n*{sec}:*\n{docs_data[country][role][sec]}\n"
        else:
            text += f"\n*{sec}*\n"

    markup = types.InlineKeyboardMarkup()
    for sec in ["Академические", "Личность", "Языковые", "Для гранта", "Дополнительно"]:
        markup.add(types.InlineKeyboardButton(sec, callback_data=f"doc_toggle_{sec}"))

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=text, parse_mode="Markdown", reply_markup=markup)

# -----------------------------
# Запуск бота
# -----------------------------
bot.infinity_polling()
