import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton
import json
from bot import handlers, database, utils  # Импорты из твоих модулей

app = Client("anime_bot", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", bot_token=os.getenv("BOT_TOKEN"))

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Напиши /art или используй инлайн: @твойбот keqing")

# Регистрируем хендлеры из bot/handlers.py (адаптируй их под pyrogram, см. ниже)
app.add_handler(handlers.router)  # Если используешь роутер, или добавь напрямую

async def main():
    await database.init_db()  # Если используешь БД
    await app.start()
    print("Bot started polling")
    await asyncio.Event().wait()  # Держим в работе

if __name__ == "__main__":
    asyncio.run(main())
