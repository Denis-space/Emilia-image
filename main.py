import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import router
from bot.database import init_db
import os

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())