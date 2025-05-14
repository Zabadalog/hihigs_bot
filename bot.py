import uuid
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from models import User, async_session, init_db
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv  # <-- добавляем

# Загружаем .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")  # <-- берём токен из переменной окружения

# FSM состояния регистрации
class Register(StatesGroup):
    choosing_role = State()
    entering_code = State()


# Команда /start
async def cmd_start(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Преподаватель")],
            [KeyboardButton(text="Слушатель")]
        ],
        resize_keyboard=True
    )
    await message.answer("Вы преподаватель или слушатель?", reply_markup=keyboard)
    await state.set_state(Register.choosing_role)

# Выбор роли
async def role_chosen(message: types.Message, state: FSMContext):
    role = message.text.lower()
    userid = str(message.from_user.id)
    username = message.from_user.username or "unknown"

    async with async_session() as session:
        result = await session.execute(select(User).where(User.userid == userid))
        user = result.scalar_one_or_none()

        if user:
            await message.answer("Вы уже зарегистрированы.", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return

        if role == "преподаватель":
            tutorcode = str(uuid.uuid4())[:8]
            session.add(User(userid=userid, username=username, tutorcode=tutorcode))
            await session.commit()
            await message.answer(f"Вы зарегистрированы как преподаватель. Ваш код: {tutorcode}", reply_markup=ReplyKeyboardRemove())
            await state.clear()
        elif role == "слушатель":
            await message.answer("Введите код преподавателя:")
            await state.set_state(Register.entering_code)
        else:
            await message.answer("Пожалуйста, выберите корректную роль.")

# Ввод кода преподавателя
async def code_entered(message: types.Message, state: FSMContext):
    code = message.text.strip()
    userid = str(message.from_user.id)
    username = message.from_user.username or "unknown"

    async with async_session() as session:
        result = await session.execute(select(User).where(User.tutorcode == code))
        tutor = result.scalar_one_or_none()

        if tutor:
            session.add(User(userid=userid, username=username, subscribe=tutor.username))
            await session.commit()
            await message.answer(f"Вы зарегистрированы как слушатель. Преподаватель: {tutor.username}", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Код преподавателя не найден. Попробуйте снова.")

    await state.clear()

# Команда /status
async def cmd_status(message: types.Message):
    userid = str(message.from_user.id)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.userid == userid))
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("Вы не зарегистрированы. Используйте команду /start.")
            return

        if user.tutorcode:
            await message.answer(f"Вы — преподаватель\nID: {user.userid}\nUsername: {user.username}\nКод для студентов: {user.tutorcode}")
        elif user.subscribe:
            await message.answer(f"Вы — слушатель\nID: {user.userid}\nUsername: {user.username}\nПодписан на: {user.subscribe}")
        else:
            await message.answer("Ваша регистрация некорректна.")

# Запуск бота
async def main():
    await init_db()
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(role_chosen, Register.choosing_role)
    dp.message.register(code_entered, Register.entering_code)
    dp.message.register(cmd_status, F.text == "/status")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())