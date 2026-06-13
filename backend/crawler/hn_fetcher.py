"""
Hacker News 采集器，通过官方 Firebase JSON API 获取 AI 相关文章
"""
import re
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from crawler.base import save_news
from crawler.filters import is_ai_related

HN_API = "https://hacker-news.firebaseio.com/v0"
FETCH_TOP_N = 100


async def _get_top_ids(client: httpx.AsyncClient) -> list[int]:
    resp = await client.get(f"{HN_API}/topstories.json", timeout=10)
    resp.raise_for_status()
    return resp.json()[:FETCH_TOP_N]


async def _get_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    try:
        resp = await client.get(f"{HN_API}/item/{item_id}.json", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


async def _fetch_og_image(client: httpx.AsyncClient, url: str) -> str:
    """抓取原文页面，提取 og:image 或第一张 <img>"""
    if not url:
        return ""
    try:
        resp = await client.get(url, timeout=8, follow_redirects=True,
                                headers={"User-Agent": "Mozilla/5.0"})
        html = resp.text[:50000]  # 只读前 50KB
        # og:image
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.IGNORECASE)
        if m:
            img = m.group(1).strip()
            if img.startswith("http"):
                return img
        # 第一张 <img>
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if m:
            img = m.group(1).strip()
            if img.startswith("http"):
                return img
    except Exception:
        pass
    return ""


async def fetch_hn(db: AsyncSession) -> int:
    """采集 Hacker News 热门中的 AI 相关文章，返回新增条数"""
    count = 0
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            ids = await _get_top_ids(client)
            for item_id in ids:
                item = await _get_item(client, item_id)
                if not item:
                    continue
                if item.get("type") != "story":
                    continue
                title = (item.get("title") or "").strip()
                url = item.get("url", "")
                if not title or not is_ai_related(title):
                    continue
                pub_time = datetime.fromtimestamp(item["time"]) if item.get("time") else datetime.now()
                image = await _fetch_og_image(client, url)
                saved = await save_news(
                    db,
                    title=title,
                    description=f"HN 评论数：{item.get('descendants', 0)}",
                    content="",
                    image=image,
                    author=item.get("by", ""),
                    source_url=url,
                    source_platform="hackernews",
                    publish_time=pub_time,
                    category_id=1,
                )
                if saved:
                    count += 1
    except Exception as e:
        print(f"[hackernews] 采集失败: {e}")
    print(f"[hackernews] 新增 {count} 条")
    return count
