from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Услуги и цены")],
            [KeyboardButton(text="📝 Сделать заказ"), KeyboardButton(text="ℹ️ О нас")],
        ],
        resize_keyboard=True,
    )

# Инлайн-клавиатура выбора услуги
def services_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Консультация — 1 000 ₽", callback_data="order_consult")],
            [InlineKeyboardButton(text="🤖 Telegram бот — от 15 000 ₽", callback_data="order_bot")],
            [InlineKeyboardButton(text="📱 Mini App — от 25 000 ₽", callback_data="order_miniapp")],
            [InlineKeyboardButton(text="🎯 Комплексное решение — от 40 000 ₽", callback_data="order_complex")],
        ]
    )

# Кнопка "Отмена"
def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить заказ")]],
        resize_keyboard=True,
    )