from aiogram import types
from sqlalchemy.future import select
from models import User, async_session

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
            await message.answer(
                f"Вы — преподаватель\nID: {user.userid}\nUsername: {user.username}\nКод для студентов: {user.tutorcode}"
            )
        elif user.subscribe:
            await message.answer(
                f"Вы — слушатель\nID: {user.userid}\nUsername: {user.username}\nПодписан на: {user.subscribe}"
            )
        else:
            await message.answer("Ваша регистрация некорректна.")