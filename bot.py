import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from src import set_my_commands, register_message_handlers
from src.handlers import router as message_router
from src.callbacks import router as callback_router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8")
    ]
)

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(message_router)
dp.include_router(callback_router)

async def main():
    logging.info("Бот запускается...")
    await set_my_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())