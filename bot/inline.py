from aiogram.types import InlineQueryResultPhoto
from bot.utils import get_booru_image
from bot.handlers import router

@router.inline_query()
async def inline_query(query: InlineQuery):
    tags = query.query.strip() or "1girl solo"
    results = []
    images = await asyncio.gather(*[get_booru_image(tags, "safe") for _ in range(10)])
    for i, img in enumerate([x for x in images if x]):
        if len(results) >= 30:
            break
        results.append(InlineQueryResultPhoto(
            id=str(i),
            photo_url=img["url"],
            thumbnail_url=img["url"],
            caption="✨"
        ))
    await query.answer(results, cache_time=1)