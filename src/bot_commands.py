from aiogram.types import BotCommand

__all__ = ['set_my_commands']

async def set_my_commands(bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="help", description="Помощь по командам"),
        BotCommand(command="status", description="Информация о пользователе"),
    ]
    await bot.set_my_commands(commands)
