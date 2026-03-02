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
        "price": 249000,
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

# ===== СОЗДАНИЕ СЧЁТА =====
@bot.message_handler(func=lambda m: any(m.text == p["title"] for p in PRODUCTS.values()))
def create_invoice(message):

    for key, product in PRODUCTS.items():
        if message.text == product["title"]:

            prices = [types.LabeledPrice(product["title"], product["price"])]

            bot.send_invoice(
                message.chat.id,
                title=product["title"],
                description=product["description"],
                provider_token=PAYMENT_TOKEN,
                currency="RUB",
                prices=prices,
                start_parameter=key,
                invoice_payload=key
            )
            break

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

    bot.send_message(
        message.chat.id,
        "Рекомендуем ознакомиться с другими продуктами.\n"
        "Также приглашаем на очные тренировки и мастер-классы."
    )

bot.polling()
