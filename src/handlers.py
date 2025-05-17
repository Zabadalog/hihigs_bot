# src/handlers.py
import uuid
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from models import User, async_session  # models.py в корне

router = Router()

class Register(StatesGroup):
    choosing_role = State()
    entering_code  = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Преподаватель")],
            [types.KeyboardButton(text="Слушатель")]
        ],
        resize_keyboard=True
    )
    await message.answer("Вы преподаватель или слушатель?", reply_markup=kb)
    await state.set_state(Register.choosing_role)

@router.message(Register.choosing_role)
async def role_chosen(message: types.Message, state: FSMContext):
    role = message.text.lower()
    uid  = message.from_user.id
    uname = message.from_user.username or "unknown"

    async with async_session() as session:
        res = await session.execute(select(User).where(User.user_id == uid))
        user_obj = res.scalar_one_or_none()

        # Если запись есть и у неё уже стоит роль (tutorcode или subscribe) — блокируем
        if user_obj and (user_obj.tutorcode or user_obj.subscribe):
            await message.answer("❗ Вы уже зарегистрированы.", reply_markup=types.ReplyKeyboardRemove())
            await state.clear()
            return

        # Иначе — регистрируем в зависимости от выбора
        if role == "преподаватель":
            code = str(uuid.uuid4())[:8]
            if user_obj:
                user_obj.tutorcode = code
                user_obj.subscribe = None
            else:
                session.add(User(user_id=uid, username=uname, tutorcode=code))
            await session.commit()

            await message.answer(
                f"✅ Вы преподаватель. Ваш код: `{code}`",
                parse_mode="Markdown",
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.clear()

        elif role == "слушатель":
            # никак не проверяем existing здесь — просто просим ввести код
            await message.answer("📝 Введите код преподавателя:")
            await state.set_state(Register.entering_code)

        else:
            await message.answer("⚠️ Пожалуйста, нажмите одну из кнопок.")

@router.message(Register.entering_code)
async def code_entered(message: types.Message, state: FSMContext):
    code = message.text.strip()
    uid  = message.from_user.id
    uname = message.from_user.username or "unknown"

    async with async_session() as session:
        res = await session.execute(select(User).where(User.tutorcode == code))
        tutor = res.scalar_one_or_none()

        if tutor:
            # создаём или обновляем слушателя
            res2 = await session.execute(select(User).where(User.user_id == uid))
            user_obj = res2.scalar_one_or_none()
            if user_obj:
                user_obj.subscribe = tutor.user_id
                user_obj.tutorcode = None
            else:
                session.add(User(user_id=uid, username=uname, subscribe=tutor.user_id))
            await session.commit()

            await message.answer(f"🎓 Вы слушатель @{tutor.username}",
                                 reply_markup=types.ReplyKeyboardRemove())
            await state.clear()
        else:
            await message.answer("❌ Неверный код, попробуйте ещё раз:")

@router.message(Command("status"))
async def cmd_status(message: types.Message, state: FSMContext):
    # 1) проверяем, не в процессе ли регистрация/смена роли
    current = await state.get_state()
    if current is not None:
        await message.answer("🔄 Вы сейчас в процессе смены роли — сначала выберите роль или введите код преподавателя.")
        return

    # 2) обычная логика
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❗ Вы не зарегистрированы. Нажмите /start")
            return

        if user.tutorcode:
            await message.answer(
                f"👨‍🏫 Вы — преподаватель\n"
                f"🆔 ID: {user.user_id}\n"
                f"📛 Username: @{user.username or 'не задан'}\n"
                f"🔑 Код для студентов: `{user.tutorcode}`",
                parse_mode="Markdown"
            )
        elif user.subscribe:
            result2 = await session.execute(select(User).where(User.user_id == user.subscribe))
            teacher = result2.scalar_one_or_none()
            if teacher:
                await message.answer(
                    f"🎓 Вы — слушатель\n"
                    f"🆔 ID: {user.user_id}\n"
                    f"📛 Username: @{user.username or 'не задан'}\n"
                    f"👨‍🏫 Подписаны на: @{teacher.username or 'не задан'}"
                )
            else:
                await message.answer(f"🎓 Вы слушатель, но преподаватель с ID {user.subscribe} не найден.")
        else:
            await message.answer("ℹ️ Невозможно определить ваш статус.")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "/start – регистрация\n"
        "/status – узнать ваш статус\n"
        "/change_role – сменить роль\n"
        "/help – это сообщение"
    )
@router.message(Command("change_role"))
async def cmd_change_role(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Очищаем старую роль в БД
    async with async_session() as session:
        res = await session.execute(select(User).where(User.user_id == user_id))
        user_obj = res.scalar_one_or_none()
        if user_obj:
            user_obj.tutorcode = None
            user_obj.subscribe = None
            await session.commit()

    # Открываем выбор новой роли
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Преподаватель")],
            [types.KeyboardButton(text="Слушатель")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите новую роль:", reply_markup=kb)
    await state.set_state(Register.choosing_role)