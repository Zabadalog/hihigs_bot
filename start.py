import uuid
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.future import select
from models import User, async_session

# FSM состояния регистрации
class Register(StatesGroup):
    choosing_role = State()
    entering_code = State()

# Команда /start
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Вы преподаватель или слушатель?", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton("Преподаватель")], [types.KeyboardButton("Слушатель")]],
        resize_keyboard=True
    ))
    await Register.choosing_role.set()

# Выбор роли
async def role_chosen(message: types.Message, state: FSMContext):
    role = message.text.lower()
    userid = str(message.from_user.id)
    username = message.from_user.username or "unknown"

    async with async_session() as session:
        result = await session.execute(select(User).where(User.userid == userid))
        user = result.scalar_one_or_none()

        if user:
            await message.answer("Вы уже зарегистрированы.", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            return

        if role == "преподаватель":
            tutorcode = str(uuid.uuid4())[:8]
            session.add(User(userid=userid, username=username, tutorcode=tutorcode))
            await session.commit()
            await message.answer(f"Вы зарегистрированы как преподаватель. Ваш код: {tutorcode}", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
        elif role == "слушатель":
            await message.answer("Введите код преподавателя:")
            await Register.entering_code.set()
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
            await message.answer(f"Вы зарегистрированы как слушатель. Преподаватель: {tutor.username}", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer("Код преподавателя не найден. Попробуйте снова.")

    await state.finish()
