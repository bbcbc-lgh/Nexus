from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_follow import UserFollow


async def list_followed_authors(db: AsyncSession, user_id: int) -> list[UserFollow]:
    result = await db.execute(
        select(UserFollow)
        .where(UserFollow.user_id == user_id, UserFollow.follow_type == "author")
        .order_by(UserFollow.created_at.desc())
    )
    return list(result.scalars().all())


async def follow_author(db: AsyncSession, user_id: int, author: str) -> bool:
    result = await db.execute(
        insert(UserFollow).values(user_id=user_id, follow_type="author", follow_value=author)
    )
    return bool(result.rowcount)


async def unfollow_author(db: AsyncSession, user_id: int, author: str) -> bool:
    result = await db.execute(
        delete(UserFollow).where(
            UserFollow.user_id == user_id,
            UserFollow.follow_type == "author",
            UserFollow.follow_value == author,
        )
    )
    return result.rowcount > 0


async def is_following_author(db: AsyncSession, user_id: int, author: str) -> bool:
    result = await db.execute(
        select(UserFollow.id).where(
            UserFollow.user_id == user_id,
            UserFollow.follow_type == "author",
            UserFollow.follow_value == author,
        )
    )
    return result.scalar_one_or_none() is not None
