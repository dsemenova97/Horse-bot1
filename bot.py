import telebot
from telebot import types
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# ===== ПРОДУКТЫ =====
PRODUCTS = {
    "guide1": {
        "title": "Гайд по молодой лошади",
        "price": 199000,  # 1990₽
        "type": "file",
        "file": "guide1.pdf",
        "description": "Пошаговая система работы с молодой лошадью"
    },
    "guide2": {
        "title": "Гайд по икс-образности",
        "price": 249000,  # 2490₽
        "type": "file",
        "file": "guide2.pdf",
        "description": "Методика коррекции задних ног"
    },
    "course1": {
        "title": "Онлайн курс по подготовке",
        "price": 990000,  # 9900₽
        "type": "course",
        "link": "https://t.me/ВАША_ССЫЛКА_НА_КАНАЛ",
        "description": "Доступ в закрытый Telegram-канал"
    }
}

# ===== ПЕРЕМЕННАЯ ДЛЯ ХРАНЕНИЯ ВЫБОРА ПОЛЬЗОВАТЕЛЯ =====
user_selection = {}  # key: chat_id, value: product_key

# ===== СТАРТ =====
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📘 Выбрать гайд", "🎓 Выбрать курс")

    bot.send_message(
        message.chat.id,
        "Добро пожаловать!\n\nВыберите действие:",
        reply_markup=markup
    )

# ===== ГАЙДЫ =====
@bot.message_handler(func=lambda m: m.text == "📘 Выбрать гайд")
def show_guides(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    text = "Доступные гайды:\n\n"

    for key in ["guide1", "guide2"]:
        product = PRODUCTS[key]
        text += f"📖 {product['title']}\n{product['description']}\nЦена: {product['price']/100}₽\n\n"
        markup.add(product["title"])

    bot.send_message(message.chat.id, text, reply_markup=markup)

# ===== КУРС =====
@bot.message_handler(func=lambda m: m.text == "🎓 Выбрать курс")
def show_course(message):
    product = PRODUCTS["course1"]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(product["title"])

    text = f"🎓 {product['title']}\n{product['description']}\nЦена: {product['price']/100}₽"

    bot.send_message(message.chat.id, text, reply_markup=markup)

# ===== ВЫБОР КОНКРЕТНОГО ПРОДУКТА =====
@bot.message_handler(func=lambda m: m.text in [p["title"] for p in PRODUCTS.values()])
def select_product(message):
    chat_id = message.chat.id
    selected_key = None
    for key, product in PRODUCTS.items():
        if message.text == product["title"]:
            selected_key = key
            break

    if not selected_key:
        return

    user_selection[chat_id] = selected_key

    product = PRODUCTS[selected_key]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💳 Оплатить")  # кнопка для оплаты

    bot.send_message(
        chat_id,
        f"Вы выбрали {product['title']}.\n{product['description']}\nЦена: {product['price']/100}₽\nНажмите кнопку, чтобы оплатить.",
        reply_markup=markup
    )

# ===== СОЗДАНИЕ СЧЁТА =====
@bot.message_handler(func=lambda m: m.text == "💳 Оплатить")
def create_invoice(message):
    chat_id = message.chat.id
    product_key = user_selection.get(chat_id)

    if not product_key:
        bot.send_message(chat_id, "Сначала выберите гайд или курс.")
        return

    product = PRODUCTS[product_key]

    prices = [types.LabeledPrice(product["title"], product["price"])]

    bot.send_invoice(
        chat_id,
        title=product["title"],
        description=product["description"],
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter=product_key,
        invoice_payload=product_key
    )

# ===== ПОДТВЕРЖДЕНИЕ ПЕРЕД ОПЛАТОЙ =====
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ===== УСПЕШНАЯ ОПЛАТА =====
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    payload = message.successful_payment.invoice_payload
    product = PRODUCTS.get(payload)

    if not product:
        return

    bot.send_message(message.chat.id, "Спасибо за покупку!")

    if product["type"] == "file":
        bot.send_document(
            message.chat.id,
            open(product["file"], "rb")
        )

    elif product["type"] == "course":
        bot.send_message(
            message.chat.id,
            f"Вот ссылка на закрытый канал:\n{product['link']}"
        )

    # Предложение ознакомиться с другими продуктами
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📘 Выбрать гайд", "🎓 Выбрать курс")
    bot.send_message(
        message.chat.id,
        "Рекомендуем ознакомиться с другими продуктами.\nТакже приглашаем на очные тренировки и мастер-классы.",
        reply_markup=markup
    )

bot.polling()