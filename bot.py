import telebot
from telebot import types

# ---------- Настройки бота ----------
BOT_TOKEN = "ВАШ_BOT_TOKEN"
PAYMENT_TOKEN = "ВАШ_TEST_PROVIDER_TOKEN"  # Тестовый токен YooKassa
CURRENCY = "RUB"

bot = telebot.TeleBot(BOT_TOKEN)

# ---------- Состояние пользователей ----------
user_data = {}  # {chat_id: {"paid_products": [], "gift_taken": False}}

# ---------- Данные продуктов ----------
GUIDES = {
    "trust": {
        "title": "С нуля к доверию",
        "short_desc": "Этот гайд поможет выстроить доверительные отношения с вашей лошадью с самого начала",
        "long_desc": "Развернутое описание гида С нуля к доверию...",
        "price": 3999,
        "file": "guide_trust.pdf",
        "cover": "cover_trust.jpg"
    },
    "hands": {
        "title": "Гайд по основам работы в руках",
        "short_desc": "Изучите основы работы с лошадью в руках: техники, упражнения и важные нюансы",
        "long_desc": "Развернутое описание гида по работе в руках...",
        "price": 2499,
        "file": "guide_hands.pdf",
        "cover": "cover_hands.jpg"
    }
}

COURSE = {
    "title": "Мини теоретический курс",
    "short_desc": "Онлайн курс по Безопасной верховой езде поможет освоить навыки взаимодействия с лошадью с лёгкостью и безопасностью",
    "long_desc": "Развернутое описание курса: аллюры, баланс, психология, аварийное управление...",
    "price": 5499,
    "link": "https://t.me/+закрытый_канал",
    "cover": "course_cover.jpg"
}

GIFTS = {
    "ryss": {"title": "Учебная рысь без боли", "file": "gift_ryss.pdf"},
    "hands_note": {"title": "Памятка по работе в руках", "file": "gift_hands.pdf"}
}

# ---------- Кнопки для навигации ----------
def main_menu_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("Все продукты 🛍️", callback_data="all_products"),
        types.InlineKeyboardButton("Выбрать гайд 📚", callback_data="choose_guide")
    )
    kb.add(
        types.InlineKeyboardButton("Выбрать курс 🎓", callback_data="choose_course"),
        types.InlineKeyboardButton("Мини-подарки 🎁", callback_data="mini_gifts")
    )
    return kb

def back_menu_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🔙 Назад", callback_data="back"),
        types.InlineKeyboardButton("🔄 Вернуться к выбору продукта", callback_data="main_menu")
    )
    return kb

# ---------- Приветственное сообщение ----------
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_data.setdefault(chat_id, {"paid_products": [], "gift_taken": False})

    bot.send_photo(
        chat_id,
        photo=open("welcome.jpg", "rb"),
        caption="👋 Привет! Я рада видеть тебя здесь! 💖🐴\n\nВыбирай продукт, который тебе интересен:",
        reply_markup=main_menu_keyboard()
    )

# ---------- Обработчик кнопок ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_data.setdefault(chat_id, {"paid_products": [], "gift_taken": False})

    if call.data == "main_menu":
        bot.edit_message_caption(chat_id, call.message.message_id, "Выбирай продукт:", reply_markup=main_menu_keyboard())

    elif call.data == "choose_guide":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(f"Подробнее о '{GUIDES['trust']['title']}' 📖", callback_data="detail_trust"))
        kb.add(types.InlineKeyboardButton(f"Подробнее о '{GUIDES['hands']['title']}' 📖", callback_data="detail_hands"))
        kb.add(types.InlineKeyboardButton("Хочу сразу оплатить 💳", callback_data="pay_guide"))
        text = ""
        for key in GUIDES:
            guide = GUIDES[key]
            text += f"**{guide['title']}**\n{guide['short_desc']}\nЦена: 💰{guide['price']}\n\n"
        bot.edit_message_text(chat_id, call.message.message_id, text, reply_markup=kb, parse_mode="Markdown")

    elif call.data.startswith("detail_"):
        key = call.data.split("_")[1]
        guide = GUIDES[key]
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💳 Оплатить", callback_data=f"pay_{key}"))
        bot.send_photo(chat_id, photo=open(guide['cover'], "rb"), caption=guide['long_desc'], reply_markup=kb)

    elif call.data.startswith("pay_"):
        key = call.data.split("_")[1]
        guide = GUIDES[key]
        user_data[chat_id]["paid_products"].append(key)
        # Здесь должна быть логика отправки счета через Telegram Payments API
        bot.send_message(chat_id, f"Спасибо! Я рада, что вам откликается мой подход 💖\nВы выбрали '{guide['title']}'")
        bot.send_document(chat_id, open(guide['file'], "rb"))
        bot.send_message(chat_id, "Спасибо за покупку! 💖")
        # Проверка мини-подарков
        if not user_data[chat_id]["gift_taken"]:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("Забрать подарок 🎁", callback_data="get_gifts"))
            bot.send_message(chat_id, "Кажется, вы забыли забрать мини-подарки 🎁", reply_markup=kb)

    elif call.data == "choose_course":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Подробнее 📖", callback_data="detail_course"))
        kb.add(types.InlineKeyboardButton("Оплатить 💳", callback_data="pay_course"))
        bot.edit_message_text(chat_id, call.message.message_id, f"{COURSE['short_desc']}\nЦена: 💰{COURSE['price']}", reply_markup=kb)

    elif call.data == "detail_course":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💳 Оплатить", callback_data="pay_course"))
        bot.send_photo(chat_id, photo=open(COURSE['cover'], "rb"), caption=COURSE['long_desc'], reply_markup=kb)

    elif call.data == "pay_course":
        user_data[chat_id]["paid_products"].append("course")
        # Здесь должна быть логика отправки счета через Telegram Payments API
        bot.send_message(chat_id, f"Спасибо! 💖 Ссылка на курс: {COURSE['link']}")
        # Проверка мини-подарков
        if not user_data[chat_id]["gift_taken"]:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("Забрать подарок 🎁", callback_data="get_gifts"))
            bot.send_message(chat_id, "Кажется, вы забыли забрать мини-подарки 🎁", reply_markup=kb)

    elif call.data == "mini_gifts" or call.data == "get_gifts":
        kb = types.InlineKeyboardMarkup()
        for key in GIFTS:
            kb.add(types.InlineKeyboardButton(f"Получить '{GIFTS[key]['title']}'", callback_data=f"gift_{key}"))
        bot.send_message(chat_id, "Вот ваши мини-подарки 🎁", reply_markup=kb)

    elif call.data.startswith("gift_"):
        key = call.data.split("_")[1]
        user_data[chat_id]["gift_taken"] = True
        bot.send_document(chat_id, open(GIFTS[key]['file'], "rb"))
        bot.send_message(chat_id, f"Вы получили '{GIFTS[key]['title']}' 🎁")

    elif call.data == "back":
        bot.send_message(chat_id, "Возвращаемся назад", reply_markup=back_menu_keyboard())

# ---------- Запуск бота ----------
bot.infinity_polling()