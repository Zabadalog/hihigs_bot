import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "button_pressed")
async def on_button(callback: CallbackQuery):
    logging.info(f"Callback 'button_pressed' от @{callback.from_user.username} ({callback.from_user.id})")
    await callback.answer("Кнопка нажата")
    await callback.message.answer("Обработка выполнена")
