import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import gspread
from google.oauth2.service_account import Credentials

# Настройки
BOT_TOKEN = "8093213579:AAFvo5tngek9K-x-DDrbI8ibV8sMBPfnnIg"
CHANNEL_ID = "@dramandraman"  # ID вашего канала
ADMIN_ID = "5365932431"  # ID администратора @draman_tt

# Google Sheets конфигурация
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "hazel-champion-466216-s8",
    "private_key_id": "e10665e7d80ffed30bd46e6cc575483795418879",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDPMbRdiX/2WPXN\nL05oeLyGwPLQArzeOJWbWBzv5nZuRGKoKQ6P3IS9FzmQSMHRh/5A+7RBWiMfadhu\nuROIZ5Dv4HUi9C/rW5f0vVxt1/bH4OiwJdedEsj/SudfZm8wdKxE0YwWSXSqApyf\nei/HNoDbMM4FdI9odtcWAHrPlT4wvfxHPvm1I4wB4VfvOb1natDniOgnZcc/r8DG\n+lIQy8qiTFkJf6fS3cJ2BwfyZxq34asDeE3CkSmUR2zX1CbpZb4ed5M4TQRjDUTX\nhJx5z1OYVB9lo2RXBxmWgnUpYNoITUYoSV7meqqxNxIdHlDF8GEuxjD2Be2PZfYo\ng0tqQLWbAgMBAAECggEACIFd8GPXSzZ33kGD/CyBcYPhk9UA8Ghg1jzF11Oqs4UY\nJBbak6112RaA4btMeLyWtqkxsZsXJQN6nU6SQcyELR/imLNu28A2gTDCzUZXyZKI\nfftxTSMUk2V9d2bKx36KnqD+TK3p3ZuRo8eBLZhyerNkSa7Xi9TEQisPEsI2iHHS\nv+5dBXL00Ak3TrePSknb3YCk2pPblvLxwNXO6gklBllNGClhyWYNyB6lDknQgx3V\nlRavB1oAe84+CXz1EM98H+q5J017uCNajbKgeLwfCTbqamnZDt4ueaPVMb6brki3\n572s8NB56dyY+cf/RrO3ptk7JdnM0wz+ILyfqquvhQKBgQD36Hf426oKVKL+3cLi\nUm2WOYsV2RarZPVHLWQnrmDE36gqwYCqTveeIiEtHDCbmlsjRY5QzlaJg2SrEKNn\nbVSm+M/ghEMzI0OWOixkuiU+aumrgvGuDnqwQibB4yNnf49TizeXZ9ImZQMuvbFN\nmAAfpsp9SVnyIla/56B7JpiOLwKBgQDV9QdLstVpmlLcDFkUoM7HM4FD/M5ku/h1\nuDFQVpgQXIRHuFv7eKDq07qUdKusI/kDajBa1Q2CFNURwR617xjLdZUFiOGckYLM\n+WaqW+mOFH+3omGaM379gWUlZd6wHstsRAYOxw+2J/m5kBxN+QDiXkSmOJhaii9s\nq7ampx6AVQKBgQCVMrFRclJJ2VonbStmrhkJ+iO8yGQeTqpXZfgK8aWHlttMsBxR\nYykfYIb68SZH34POHIRkGWp3ZD5nvaG6E1CJFOF2y+LtmeGJPgWNsYHMqOdss2fk\nSw6Hmahds+eQ2HJX40dXtcICHXTm4n8cpcgdRHJFKKobUZNH94zb0QSrPQKBgQDH\nD3fAOBxSaiBZVquyg4Ke1w6XYKfuFOyvKbXH1ykXX9w6lg4OQ0cD9AWNhZcLS1Ss\nlqlyePJeal9qa1DVWCSrdzQ0uAugDcmyRv/71BPR+sRw54UDYJHv7elbCBJNrfj5\nO7ifGxlFEqBGwwtyiA8IjUg1lkY5RoOlCYWgO7AnGQKBgGE8a4aqYxAesi75xFui\n4ij9vtwOlX0/KKqbhUa/OxFofjCRJkNl8HfQJFsTfsSYcXk5bLD8cZWh4+nFRO1o\nIyq7MqVfxiIoBdwCLLHJlP/DfJIPDuC6IrtxT756QxvFSWIZ8HKGS9mw2z/0ro1M\nCa8nYO+SSHIyyB/kK4op1Yyc\n-----END PRIVATE KEY-----\n",
    "client_email": "id-theater-bot-service@hazel-champion-466216-s8.iam.gserviceaccount.com",
    "client_id": "117654592038716556949",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-theater-bot-service%40hazel-champion-466216-s8.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для FSM
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_year = State()
    waiting_for_phone = State()
    waiting_for_seats = State()
    waiting_for_confirmation = State()

# Хранилище данных о спектаклях
shows_data: Dict[str, Dict[str, Any]] = {}

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Google Sheets API
def get_google_sheets_client():
    """Подключение к Google Sheets API"""
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=scope)
    client = gspread.authorize(creds)
    return client

def extract_sheet_id(url: str) -> str:
    """Извлечение ID таблицы из URL"""
    import re
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else ""

async def check_user_subscription(user_id: int) -> bool:
    """Проверка подписки на канал"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

async def check_user_has_username(user: types.User) -> bool:
    """Проверка наличия username у пользователя"""
    return user.username is not None and user.username.strip() != ""

def add_registration_to_sheet(sheet_url: str, user_data: dict) -> bool:
    """Добавление данных в Google Таблицу"""
    try:
        client = get_google_sheets_client()
        sheet_id = extract_sheet_id(sheet_url)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.get_worksheet(0)  # Первый лист
        
        # Формирование строки данных
        row_data = [
            datetime.now().strftime("%d.%m.%Y %H:%M:%S"),  # Дата заявки
            f"@{user_data['username']}",  # Username
            user_data['surname'],  # Фамилия
            user_data['name'],  # Имя
            user_data['birth_year'],  # Год рождения
            user_data['phone'],  # Телефон
            user_data['seats']  # Количество мест
        ]
        
        worksheet.append_row(row_data)
        return True
        
    except Exception as e:
        logger.error(f"Ошибка записи в таблицу: {e}")
        return False

def check_duplicate_registration(sheet_url: str, username: str, phone: str) -> bool:
    """Проверка на дублирование заявок"""
    try:
        client = get_google_sheets_client()
        sheet_id = extract_sheet_id(sheet_url)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.get_worksheet(0)
        
        all_records = worksheet.get_all_records()
        
        for record in all_records:
            if (record.get('Username', '').lower() == f"@{username}".lower() or 
                record.get('Телефон', '') == phone):
                return True
        return False
        
    except Exception as e:
        logger.error(f"Ошибка проверки дубликатов: {e}")
        return False

# Команды для администратора
@dp.message(Command("add_show"))
async def add_show_command(message: Message):
    """Команда для добавления нового спектакля (только для админа)"""
    if str(message.from_user.id) != ADMIN_ID:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    await message.answer(
        "📝 Для добавления спектакля отправьте данные в формате:\n\n"
        "Название спектакля\n"
        "Дата и время\n"
        "Ссылка на Google Таблицу\n\n"
        "Пример:\n"
        "Гамлет\n"
        "25.07.2025 19:00\n"
        "https://docs.google.com/spreadsheets/d/..."
    )

@dp.message(F.text.contains("docs.google.com/spreadsheets"))
async def process_show_data(message: Message):
    """Обработка данных о спектакле от админа"""
    if str(message.from_user.id) != ADMIN_ID:
        return
    
    lines = message.text.strip().split('\n')
    if len(lines) < 3:
        await message.answer("❌ Неправильный формат. Нужно 3 строки: название, дата/время, ссылка.")
        return
    
    show_name = lines[0].strip()
    show_datetime = lines[1].strip()
    sheet_url = lines[2].strip()
    
    # Создание поста о спектакле
    keyboard = InlineKeyboardBuilder()
    callback_data = f"register_{len(shows_data)}"
    keyboard.add(InlineKeyboardButton(text="🎭 Регистрация", callback_data=callback_data))
    
    # Сохранение данных о спектакле
    shows_data[callback_data] = {
        'name': show_name,
        'datetime': show_datetime,
        'sheet_url': sheet_url
    }
    
    post_text = f"🎭 **{show_name}**\n\n📅 {show_datetime}\n\n🎫 Бесплатные билеты!\nДля регистрации нажмите кнопку ниже ⬇️"
    
    try:
        await bot.send_message(
            CHANNEL_ID,
            post_text,
            reply_markup=keyboard.as_markup(),
            parse_mode="Markdown"
        )
        await message.answer("✅ Пост о спектакле опубликован в канале!")
    except Exception as e:
        await message.answer(f"❌ Ошибка публикации: {e}")

# Обработка нажатия на кнопку регистрации
@dp.callback_query(F.data.startswith("register_"))
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    """Начало процесса регистрации"""
    show_id = callback.data
    
    if show_id not in shows_data:
        await callback.answer("❌ Спектакль не найден", show_alert=True)
        return
    
    user = callback.from_user
    
    # Проверка подписки на канал
    if not await check_user_subscription(user.id):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        keyboard.add(InlineKeyboardButton(text="✅ Я подписался", callback_data=show_id))
        
        await callback.message.answer(
            "❗️ Для регистрации необходимо подписаться на наш канал:",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
        return
    
    # Проверка наличия username
    if not await check_user_has_username(user):
        await callback.message.answer(
            "❗️ Для регистрации необходимо создать имя пользователя (никнейм) в Telegram:\n\n"
            "1. Откройте Настройки → Изменить профиль\n"
            "2. Создайте имя пользователя\n"
            "3. Вернитесь и нажмите на кнопку регистрации снова"
        )
        await callback.answer()
        return
    
    # Проверка на дублирование
    sheet_url = shows_data[show_id]['sheet_url']
    if check_duplicate_registration(sheet_url, user.username, ""):
        await callback.message.answer("❌ Вы уже подали заявку на этот спектакль!")
        await callback.answer()
        return
    
    # Сохранение данных о спектакле в состоянии
    await state.update_data(show_id=show_id, user_id=user.id, username=user.username)
    
    # Начало сбора данных
    await callback.message.answer(
        f"🎭 Регистрация на **{shows_data[show_id]['name']}**\n\n"
        "Введите вашу фамилию и имя (через пробел):\n"
        "Например: Петров Иван",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.waiting_for_name)
    await callback.answer()

# Обработка ввода фамилии и имени
@dp.message(StateFilter(Registration.waiting_for_name))
async def process_name(message: Message, state: FSMContext):
    """Обработка фамилии и имени"""
    name_parts = message.text.strip().split()
    
    if len(name_parts) < 2:
        await message.answer("❌ Пожалуйста, введите фамилию и имя через пробел.\nНапример: Петров Иван")
        return
    
    surname = name_parts[0]
    name = " ".join(name_parts[1:])
    
    await state.update_data(surname=surname, name=name)
    await message.answer("📅 Введите ваш год рождения (4 цифры):\nНапример: 1990")
    await state.set_state(Registration.waiting_for_birth_year)

# Обработка года рождения
@dp.message(StateFilter(Registration.waiting_for_birth_year))
async def process_birth_year(message: Message, state: FSMContext):
    """Обработка года рождения"""
    try:
        birth_year = int(message.text.strip())
        current_year = datetime.now().year
        
        if birth_year < 1900 or birth_year > current_year - 5:
            await message.answer("❌ Пожалуйста, введите корректный год рождения (например: 1990)")
            return
            
    except ValueError:
        await message.answer("❌ Пожалуйста, введите год рождения цифрами (например: 1990)")
        return
    
    await state.update_data(birth_year=birth_year)
    await message.answer("📱 Введите ваш номер телефона:\nНапример: +380501234567 или 0501234567")
    await state.set_state(Registration.waiting_for_phone)

# Обработка номера телефона
@dp.message(StateFilter(Registration.waiting_for_phone))
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    phone = message.text.strip()
    
    # Базовая валидация телефона
    if len(phone) < 10:
        await message.answer("❌ Пожалуйста, введите корректный номер телефона")
        return
    
    # Проверка на дублирование по телефону
    data = await state.get_data()
    show_id = data['show_id']
    sheet_url = shows_data[show_id]['sheet_url']
    
    if check_duplicate_registration(sheet_url, "", phone):
        await message.answer("❌ Этот номер телефона уже использовался для регистрации на данный спектакль!")
        await state.clear()
        return
    
    await state.update_data(phone=phone)
    
    # Кнопки для выбора количества мест
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="1 место", callback_data="seats_1"))
    keyboard.add(InlineKeyboardButton(text="2 места", callback_data="seats_2"))
    keyboard.adjust(2)
    
    await message.answer(
        "🎫 Выберите количество мест:",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(Registration.waiting_for_seats)

# Обработка выбора количества мест
@dp.callback_query(StateFilter(Registration.waiting_for_seats), F.data.startswith("seats_"))
async def process_seats(callback: types.CallbackQuery, state: FSMContext):
    """Обработка количества мест"""
    seats = callback.data.split("_")[1]
    await state.update_data(seats=seats)
    
    # Получение всех данных для подтверждения
    data = await state.get_data()
    show_id = data['show_id']
    show_info = shows_data[show_id]
    
    confirmation_text = (
        f"📝 **Подтверждение данных**\n\n"
        f"🎭 Спектакль: {show_info['name']}\n"
        f"📅 Дата: {show_info['datetime']}\n\n"
        f"👤 Фамилия Имя: {data['surname']} {data['name']}\n"
        f"📅 Год рождения: {data['birth_year']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🎫 Количество мест: {seats}\n\n"
        f"Всё верно?"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"))
    keyboard.add(InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_no"))
    keyboard.adjust(2)
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.waiting_for_confirmation)
    await callback.answer()

# Обработка подтверждения
@dp.callback_query(StateFilter(Registration.waiting_for_confirmation))
async def process_confirmation(callback: types.CallbackQuery, state: FSMContext):
    """Обработка подтверждения регистрации"""
    if callback.data == "confirm_yes":
        data = await state.get_data()
        show_id = data['show_id']
        sheet_url = shows_data[show_id]['sheet_url']
        
        # Попытка записи в таблицу
        if add_registration_to_sheet(sheet_url, data):
            await callback.message.edit_text(
                "✅ **Заявка принята!**\n\n"
                "Спасибо за регистрацию. Мы свяжемся с вами для подтверждения бронирования.",
                parse_mode="Markdown"
            )
            
            # Уведомление админа
            try:
                admin_text = (
                    f"🔔 **Новая заявка**\n\n"
                    f"🎭 Спектакль: {shows_data[show_id]['name']}\n"
                    f"👤 {data['surname']} {data['name']}\n"
                    f"📱 {data['phone']}\n"
                    f"🎫 Мест: {data['seats']}\n"
                    f"👤 @{data['username']}"
                )
                await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления админу: {e}")
                
        else:
            await callback.message.edit_text(
                "❌ Произошла ошибка при обработке заявки. Попробуйте позже или обратитесь к администратору."
            )
    else:
        await callback.message.edit_text("❌ Регистрация отменена.")
    
    await state.clear()
    await callback.answer()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка команды /start"""
    await message.answer(
        "🎭 Добро пожаловать в бот театра DRAMAN!\n\n"
        "Для регистрации на спектакли следите за постами в канале @dramandraman "
        "и нажимайте кнопку 'Регистрация' под постом о спектакле."
    )

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Справка по использованию бота"""
    help_text = (
        "🎭 **Помощь по использованию бота**\n\n"
        "**Для зрителей:**\n"
        "• Подпишитесь на канал @dramandraman\n"
        "• Создайте никнейм в Telegram (если нет)\n"
        "• Нажмите 'Регистрация' под постом о спектакле\n"
        "• Заполните данные\n\n"
        "**Ограничения:**\n"
        "• Максимум 2 места на заявку\n"
        "• Одна заявка на спектакль от пользователя\n\n"
        "По вопросам: @draman_tt"
    )
    await message.answer(help_text, parse_mode="Markdown")

# Основная функция запуска
async def main():
    """Запуск бота"""
    logger.info("Запуск бота...")
    
    # Удаление вебхука (для polling)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())