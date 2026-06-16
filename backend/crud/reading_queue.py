from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.reading_queue import ReadingQueue
from models.news import News


async def check_in_queue(db: AsyncSession, user_id: int, news_id: int) -> bool:
    result = await db.execute(
        select(ReadingQueue).where(ReadingQueue.user_id == user_id, ReadingQueue.news_id == news_id)
    )
    return result.scalar_one_or_none() is not None


async def add_to_queue(db: AsyncSession, user_id: int, news_id: int):
    item = ReadingQueue(user_id=user_id, news_id=news_id)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def remove_from_queue(db: AsyncSession, user_id: int, news_id: int) -> bool:
    result = await db.execute(
        delete(ReadingQueue).where(ReadingQueue.user_id == user_id, ReadingQueue.news_id == news_id)
    )
    return result.rowcount > 0


async def get_queue(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10):
    stmt = (
        select(News, ReadingQueue.created_at.label("queue_time"))
        .join(ReadingQueue, ReadingQueue.news_id == News.id)
        .where(ReadingQueue.user_id == user_id)
        .order_by(ReadingQueue.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()


async def get_queue_count(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.count(ReadingQueue.id)).where(ReadingQueue.user_id == user_id)
    )
    return result.scalar_one()


async def clear_queue(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        delete(ReadingQueue).where(ReadingQueue.user_id == user_id)
    )
    return result.rowcount
