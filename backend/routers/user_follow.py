from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_conf import get_db
from utils.response import success_response
from utils.security import get_current_user
from schemas.user_follow import FollowAuthorIn
from crud.user_follow import (
    follow_author,
    is_following_author,
    list_followed_authors,
    unfollow_author,
)

router = APIRouter(prefix="/api/follow", tags=["follow"])


@router.get("/authors", summary="获取关注作者列表")
async def list_authors(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await list_followed_authors(db, current_user.id)
    return success_response({
        "list": [
            {"author": item.follow_value, "createdAt": item.created_at}
            for item in items
        ]
    })


@router.get("/author/check", summary="检查是否关注作者")
async def check_author(
    author: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return success_response({"following": await is_following_author(db, current_user.id, author.strip())})


@router.post("/author", summary="关注作者")
async def follow_author_endpoint(
    body: FollowAuthorIn,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    author = body.author.strip()
    if not await is_following_author(db, current_user.id, author):
        await follow_author(db, current_user.id, author)
    return success_response(message="已关注")


@router.delete("/author", summary="取消关注作者")
async def unfollow_author_endpoint(
    author: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await unfollow_author(db, current_user.id, author.strip())
    return success_response(message="已取消关注")
