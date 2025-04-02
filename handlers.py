import logging
from aiogram import types, Router, F
from aiogram.filters import Command
from .keyboard import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


async def process_start_command(message: types.Message):
    logging.info(f"/start от @{message.from_user.username} ({message.from_user.id})")
    await message.answer(
        f"Привет, {message.from_user.first_name}!",
        reply_markup=keyboard
    )


async def process_help_command(message: types.Message):
    logging.info(f"/help от @{message.from_user.username} ({message.from_user.id})")
    await message.answer(
        "/start – запуск бота\n"
        "/help – справка\n"
        "/status – информация о пользователе"
    )


async def process_status_command(message: types.Message):
    logging.info(f"/status от @{message.from_user.username} ({message.from_user.id})")
    await message.answer(
        f"ID: {message.from_user.id}\n"
        f"Username: @{message.from_user.username or 'не указан'}"
    )


@router.message(Command("start"))
async def handle_start(message: types.Message):
    await process_start_command(message)


@router.message(Command("help"))
async def handle_help(message: types.Message):
    await process_help_command(message)


@router.message(Command("status"))
async def handle_status(message: types.Message):
    await process_status_command(message)


@router.message(F.text == "Статус")
async def button_status(message: types.Message):
    logging.info(f"Нажата кнопка 'Статус' от @{message.from_user.username}")
    await process_status_command(message)


@router.message(F.text == "Помощь")
async def button_help(message: types.Message):
    logging.info(f"Нажата кнопка 'Помощь' от @{message.from_user.username}")
    await process_help_command(message)
