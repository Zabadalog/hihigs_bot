from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Статус"), KeyboardButton(text=" Помощь")]
    ],
    resize_keyboard=True
)
