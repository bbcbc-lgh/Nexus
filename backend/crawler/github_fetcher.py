from datetime import datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from crawler.base import save_news
from crawler.filters import is_ai_related
from crud.topic_tag import infer_and_tag


GITHUB_SEARCH = "https://api.github.com/search/repositories"
QUERIES = [
    "topic:llm stars:>100",
    "topic:artificial-intelligence stars:>100",
    "topic:machine-learning stars:>100",
]
MAX_RESULTS_PER_QUERY = 3


def _parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return datetime.now()


async def fetch_github_ai(db: AsyncSession) -> int:
    items = []
    seen = set()
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            for query in QUERIES:
                resp = await client.get(
                    GITHUB_SEARCH,
                    params={
                        "q": query,
                        "sort": "updated",
                        "order": "desc",
                        "per_page": str(MAX_RESULTS_PER_QUERY),
                    },
                    headers={
                        "Accept": "application/vnd.github+json",
                        "User-Agent": "NexusNews/1.0 (local personal news reader)",
                    },
                )
                resp.raise_for_status()
                for repo in resp.json().get("items", []):
                    full_name = repo.get("full_name")
                    if full_name and full_name not in seen:
                        seen.add(full_name)
                        items.append(repo)
    except Exception as e:
        print(f"[github_ai] request failed: {e}")
        return 0

    count = 0
    for repo in items:
        full_name = repo.get("full_name") or ""
        description = repo.get("description") or ""
        if not full_name:
            continue
        if not is_ai_related(full_name, description):
            continue
        stars = int(repo.get("stargazers_count") or 0)
        forks = int(repo.get("forks_count") or 0)
        title = f"{full_name}: {description}" if description else full_name
        saved = await save_news(
            db,
            title=title,
            description=description,
            content="",
            image=repo.get("owner", {}).get("avatar_url") or "",
            author=repo.get("owner", {}).get("login") or "GitHub",
            source_url=repo.get("html_url") or "",
            source_platform="github_ai",
            publish_time=_parse_date(repo.get("pushed_at") or repo.get("updated_at")),
            category_id=1,
            external_id=full_name,
            source_score=stars,
            source_comment_count=forks,
        )
        if saved:
            await infer_and_tag(db, saved, f"{title} {description} github open source llm")
            count += 1

    print(f"[github_ai] inserted {count}")
    return count
