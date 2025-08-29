import asyncio
import httpx

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
KEYWORDS = ["AI", "Machine Learning", "Deep Learning"]


async def fetch_story(client: httpx.AsyncClient, item_id: int):
    try:
        resp = await client.get(ITEM_URL.format(item_id), timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


async def fetch_top_stories(limit: int = 100):
    async with httpx.AsyncClient() as client:
        resp = await client.get(TOP_STORIES_URL, timeout=5.0)
        resp.raise_for_status()
        top_ids = resp.json()[:limit]

        # 并发抓取
        tasks = [fetch_story(client, item_id) for item_id in top_ids]
        stories = await asyncio.gather(*tasks)
        return [s for s in stories if s is not None]


async def main():
    print("Fetching top Hacker News stories...")
    stories = await fetch_top_stories(100)
    ai_stories = [
        {
            "title": s["title"],
            "url": s.get("url", f"https://news.ycombinator.com/item?id={s['id']}"),
        }
        for s in stories
        if any(k.lower() in s.get("title", "").lower() for k in KEYWORDS)
    ]

    print(f"Found {len(ai_stories)} AI-related stories:\n")
    for story in ai_stories:
        print(f"- {story['title']}")
        print(f"  Link: {story['url']}\n")


if __name__ == "__main__":
    asyncio.run(main())
