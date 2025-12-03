from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultPhoto
from aiogram.filters import Command
from bot.database import AsyncSessionLocal, User
from bot.utils import get_booru_image
from sqlalchemy import select, update
import json
import asyncio

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Напиши /art или используй инлайн: @твойбот keqing")

@router.message(Command("nsfw_on"))
async def nsfw_on(message: Message):
    if message.chat.type != "private":
        return await message.answer("Только в ЛС!")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == message.from_user.id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=message.from_user.id, nsfw_allowed=True)
            session.add(user)
        else:
            user.nsfw_allowed = True
        await session.commit()
    await message.answer("NSFW включён! Теперь можно /art rating:explicit")

@router.message(Command("nsfw_off"))
async def nsfw_off(message: Message):
    async with AsyncSessionLocal() as session:
        await session.execute(update(User).where(User.id == message.from_user.id).values(nsfw_allowed=False))
        await session.commit()
    await message.answer("NSFW выключен")

last_sent = {}

@router.message(F.text.startswith("/art") | F.text == "/random")
async def art_command(message: Message):
    tags = message.text.replace("/art", "").replace("/random", "").strip()
    rating = "explicit" if "rating:explicit" in tags.lower() and message.chat.type == "private" else "safe"
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.nsfw_allowed).where(User.id == message.from_user.id))
        allowed = result.scalar() or False
        if rating == "explicit" and not allowed:
            return await message.answer("Сначала включи NSFW: /nsfw_on")

    user_id = message.from_user.id
    chat_id = message.chat.id
    key = f"{user_id}:{chat_id}"
    if key in last_sent and asyncio.get_event_loop().time() - last_sent[key] < 5:
        return await message.answer("Не спамь, подожди 5 сек :)")
    last_sent[key] = asyncio.get_event_loop().time()

    await message.answer_chat_action("upload_photo")
    img = await get_booru_image(tags, rating)
    if not img:
        return await message.answer("Ничего не нашёл :(")

    sent = await message.answer_photo(img["url"], caption="✨", reply_markup=source_kb(img["source"]))
    # Сохраняем file_id
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == message.from_user.id))
        user = result.scalar_one_or_none()
        if user:
            favs = json.loads(user.favourites) if user.favourites else []
            favs.append(sent.photo[-1].file_id)
            user.favourites = json.dumps(favs[-100:])  # последние 100
            await session.commit()

def source_kb(source):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("Источник", url=source)]])