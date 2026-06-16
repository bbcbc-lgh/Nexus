from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite_folder import FavoriteFolder
from models.favorite import Favorite


async def list_folders(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(FavoriteFolder)
        .where(FavoriteFolder.user_id == user_id)
        .order_by(FavoriteFolder.created_at.asc())
    )
    return list(result.scalars().all())


async def create_folder(db: AsyncSession, user_id: int, name: str) -> FavoriteFolder:
    folder = FavoriteFolder(user_id=user_id, name=name)
    db.add(folder)
    await db.flush()
    await db.refresh(folder)
    return folder


async def rename_folder(db: AsyncSession, user_id: int, folder_id: int, name: str) -> bool:
    result = await db.execute(
        update(FavoriteFolder)
        .where(FavoriteFolder.id == folder_id, FavoriteFolder.user_id == user_id)
        .values(name=name)
    )
    return result.rowcount > 0


async def delete_folder(db: AsyncSession, user_id: int, folder_id: int) -> bool:
    # 先把该文件夹下的收藏的 folder_id 置空（解绑），再删除文件夹
    await db.execute(
        update(Favorite)
        .where(Favorite.folder_id == folder_id)
        .values(folder_id=None)
    )
    result = await db.execute(
        delete(FavoriteFolder)
        .where(FavoriteFolder.id == folder_id, FavoriteFolder.user_id == user_id)
    )
    return result.rowcount > 0


async def count_favorites_in_folder(db: AsyncSession, user_id: int, folder_id: int | None) -> int:
    stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    if folder_id is None:
        stmt = stmt.where(Favorite.folder_id.is_(None))
    else:
        stmt = stmt.where(Favorite.folder_id == folder_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def move_favorite(db: AsyncSession, user_id: int, news_id: int, folder_id: int | None) -> bool:
    result = await db.execute(
        update(Favorite)
        .where(Favorite.user_id == user_id, Favorite.news_id == news_id)
        .values(folder_id=folder_id)
    )
    return result.rowcount > 0
