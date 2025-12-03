import aiohttp
import random

async def get_booru_image(tags="", rating="safe", limit=100):
    base = "https://safebooru.org/index.php?page=dapi&s=post&json=1&q=index"
    if rating == "explicit":
        base = "https://danbooru.donmai.us/posts.json"
        tags += " rating:explicit"
    url = f"{base}&tags={tags}&limit={limit}&random=true"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if not data or isinstance(data, dict) and data.get("success") == False:
                return None
            post = random.choice(data if isinstance(data, list) else data.get("posts", []))
            if not post.get("file_url"):
                return None
            return {
                "url": "https://danbooru.donmai.us" + post["file_url"] if "danbooru" in base else post["file_url"],
                "source": f"https://danbooru.donmai.us/posts/{post['id']}" if "danbooru" in base else f"https://safebooru.org/index.php?page=post&s=view&id={post['id']}"
            }