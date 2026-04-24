import asyncio
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

import keyboards as kb
import db

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8388064114:AAGLuQH-tJkcoDjPbDsfXZsUrZvbL3R3Jk4"  # Получи в @BotFather
ADMIN_ID = 6824480691  # Твой Telegram ID (узнать в @getmyid_bot)

# ========== ПРОКСИ ==========
# Если у тебя есть SOCKS5 прокси — впиши сюда
# Если нет — оставь как есть, будет пробовать напрямую (нужен VPN)
PROXY_URL = None  # Например: "socks5://login:pass@1.2.3.4:1080"

# ========== ИНИЦИАЛИЗАЦИЯ ==========
if PROXY_URL:
    # С прокси
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=BOT_TOKEN, session=session)
else:
    # Без прокси (работает только с VPN или за границей)
    bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(storage=MemoryStorage())

# ========== СОСТОЯНИЯ FSM ==========
class OrderState(StatesGroup):
    waiting_for_service = State()
    waiting_for_name = State()
    waiting_for_phone = State()

# ========== КОМАНДЫ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для приёма заказов.\n\n"
        "Выберите действие в меню:",
        reply_markup=kb.main_menu(),
    )

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔐 Админ-панель пока в разработке")
    else:
        await message.answer("⛔ Нет доступа")

# ========== МЕНЮ ==========
@dp.message(F.text == "📋 Услуги и цены")
async def show_services(message: Message):
    text = (
        "📋 <b>Наши услуги:</b>\n\n"
        "🔧 <b>Консультация</b> — 1 000 ₽\n"
        "  · Анализ задачи, подбор решения, план работ\n\n"
        "🤖 <b>Telegram бот</b> — от 15 000 ₽\n"
        "  · Разработка бота под ключ (aiogram/Python)\n\n"
        "📱 <b>Mini App</b> — от 25 000 ₽\n"
        "  · Веб-приложение внутри Telegram\n\n"
        "🎯 <b>Комплексное решение</b> — от 40 000 ₽\n"
        "  · Бот + Mini App + интеграции\n\n"
        "<i>Для заказа нажмите кнопку «Сделать заказ»</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "ℹ️ О нас")
async def show_about(message: Message):
    await message.answer(
        "ℹ️ <b>О нас:</b>\n\n"
        "Разрабатываем Telegram-ботов и Mini Apps для бизнеса. "
        "Работаем с 2024 года, больше 30 проектов.\n\n"
        "Связь: @your_username",
        parse_mode="HTML",
    )

# ========== ОФОРМЛЕНИЕ ЗАКАЗА ==========
@dp.message(F.text == "📝 Сделать заказ")
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderState.waiting_for_service)
    await message.answer(
        "Выберите услугу:",
        reply_markup=kb.services_menu(),
    )

@dp.callback_query(F.data.startswith("order_"), StateFilter(OrderState.waiting_for_service))
async def service_chosen(callback: CallbackQuery, state: FSMContext):
    service_map = {
        "order_consult": "Консультация",
        "order_bot": "Telegram бот",
        "order_miniapp": "Mini App",
        "order_complex": "Комплексное решение",
    }
    service = service_map.get(callback.data, "Неизвестная услуга")
    await state.update_data(service=service)
    await callback.answer()
    await state.set_state(OrderState.waiting_for_name)
    await callback.message.answer(
        f"✅ Выбрано: <b>{service}</b>\n\nВведите ваше имя:",
        parse_mode="HTML",
        reply_markup=kb.cancel_keyboard(),
    )

@dp.message(StateFilter(OrderState.waiting_for_name))
async def name_entered(message: Message, state: FSMContext):
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменён", reply_markup=kb.main_menu())
        return
    await state.update_data(client_name=message.text)
    await state.set_state(OrderState.waiting_for_phone)
    await message.answer("📞 Введите ваш номер телефона:")

@dp.message(StateFilter(OrderState.waiting_for_phone))
async def phone_entered(message: Message, state: FSMContext):
    if message.text == "❌ Отменить заказ":
        await state.clear()
        await message.answer("❌ Заказ отменён", reply_markup=kb.main_menu())
        return

    data = await state.get_data()
    service = data["service"]
    client_name = data["client_name"]
    phone = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "—"

    # Сохраняем в базу
    db.save_order(user_id, username, service, client_name, phone)

    # Уведомление админу
    admin_text = (
        f"🆕 <b>Новый заказ!</b>\n\n"
        f"📌 Услуга: {service}\n"
        f"👤 Имя: {client_name}\n"
        f"📞 Телефон: {phone}\n"
        f"🆔 ID: {user_id}\n"
        f"💬 @{username}"
    )
    try:
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        print(f"Не удалось отправить админу: {e}")

    # Подтверждение клиенту
    await message.answer(
        f"✅ <b>Заказ принят!</b>\n\n"
        f"📌 {service}\n"
        f"👤 {client_name}\n"
        f"📞 {phone}\n\n"
        f"Я свяжусь с вами в ближайшее время!",
        parse_mode="HTML",
        reply_markup=kb.main_menu(),
    )
    await state.clear()

# ========== ОБРАБОТЧИК ОТМЕНЫ В ЛЮБОМ СОСТОЯНИИ ==========
@dp.message(F.text == "❌ Отменить заказ")
async def cancel_order(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("❌ Заказ отменён", reply_markup=kb.main_menu())

# ========== ЗАПУСК ==========
async def main():
    db.init_db()
    print("✅ Бот запущен!")
    
    # Удаляем вебхук на всякий случай и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")