from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from models.topic_tag import TopicTag, NewsTopicTag


async def list_tags(db: AsyncSession):
    result = await db.execute(select(TopicTag).order_by(TopicTag.name))
    return result.scalars().all()


async def get_tags_for_news(db: AsyncSession, news_id: int) -> list[TopicTag]:
    result = await db.execute(
        select(TopicTag)
        .join(NewsTopicTag, NewsTopicTag.tag_id == TopicTag.id)
        .where(NewsTopicTag.news_id == news_id)
    )
    return result.scalars().all()


async def get_news_ids_by_tag(db: AsyncSession, tag_slug: str, skip: int, limit: int) -> list[int]:
    result = await db.execute(
        select(NewsTopicTag.news_id)
        .join(TopicTag, TopicTag.id == NewsTopicTag.tag_id)
        .where(TopicTag.slug == tag_slug)
        .offset(skip).limit(limit)
    )
    return [r for r, in result.all()]


async def set_news_tags(db: AsyncSession, news_id: int, tag_ids: list[int]):
    await db.execute(
        text("DELETE FROM news_topic_tag WHERE news_id = :nid"),
        {"nid": news_id}
    )
    for tag_id in tag_ids:
        db.add(NewsTopicTag(news_id=news_id, tag_id=tag_id))
    await db.commit()


async def infer_and_tag(db: AsyncSession, news_id: int, text_content: str):
    """基于关键词规则推断标签并写入"""
    rules: list[tuple[str, list[str]]] = [
        ("llm",       ["llm", "large language model", "language model", "transformer"]),
        ("gpt",       ["gpt", "chatgpt", "gpt-4", "gpt-3", "openai"]),
        ("open-source", ["open source", "open-source", "github", "hugging face", "huggingface"]),
        ("security",  ["security", "vulnerability", "exploit", "hack", "breach", "malware", "ransomware"]),
        ("robotics",  ["robot", "robotics", "humanoid", "autonomous", "drone"]),
        ("image-gen", ["diffusion", "image generation", "dall-e", "stable diffusion", "midjourney", "text-to-image"]),
        ("code",      ["code", "coding", "programming", "compiler", "ide", "github copilot"]),
        ("search",    ["search engine", "retrieval", "rag", "vector search"]),
        ("reasoning", ["reasoning", "chain of thought", "cot", "o1", "o3", "inference"]),
        ("dataset",   ["dataset", "benchmark", "training data", "corpus"]),
        ("hardware",  ["gpu", "chip", "hardware", "nvidia", "tpu", "semiconductor"]),
        ("policy",    ["regulation", "policy", "law", "government", "congress", "eu ai act", "compliance"]),
        ("startup",   ["startup", "funding", "series a", "series b", "valuation", "vc", "venture"]),
        ("research",  ["paper", "arxiv", "research", "study", "experiment", "finding"]),
        ("release",   ["launch", "release", "announce", "introduce", "new model", "available now"]),
    ]

    lower = text_content.lower()
    matched_slugs = [slug for slug, kws in rules if any(kw in lower for kw in kws)]
    if not matched_slugs:
        return

    result = await db.execute(
        select(TopicTag.id).where(TopicTag.slug.in_(matched_slugs))
    )
    tag_ids = [r for r, in result.all()]
    await set_news_tags(db, news_id, tag_ids)
