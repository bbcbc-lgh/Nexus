from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_conf import get_db
from utils.security import get_current_user
from models.users import User
from schemas.reading_queue import QueueAdd
from utils.response import success_response
from crud.reading_queue import (
    check_in_queue,
    add_to_queue,
    remove_from_queue,
    get_queue,
    get_queue_count,
    clear_queue,
)

router = APIRouter(prefix="/api/queue", tags=["reading-queue"])


@router.get("/check", summary="检查稍后阅读状态")
async def check_queue_status(
    newsId: int = Query(..., alias="newsId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    in_queue = await check_in_queue(db, user_id=current_user.id, news_id=newsId)
    return success_response({"inQueue": in_queue})


@router.post("/add", summary="加入稍后阅读")
async def add_to_queue_endpoint(
    body: QueueAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    already = await check_in_queue(db, user_id=current_user.id, news_id=body.newsId)
    if already:
        raise HTTPException(status_code=400, detail="已在队列中")
    item = await add_to_queue(db, user_id=current_user.id, news_id=body.newsId)
    return success_response({
        "id": item.id,
        "userId": item.user_id,
        "newsId": item.news_id,
        "createTime": item.created_at,
    }, "已加入稍后阅读")


@router.delete("/remove", summary="移出稍后阅读")
async def remove_from_queue_endpoint(
    newsId: int = Query(..., alias="newsId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await remove_from_queue(db, user_id=current_user.id, news_id=newsId)
    if not removed:
        raise HTTPException(status_code=404, detail="记录不存在")
    return success_response(message="已从队列移除")


@router.get("/list", summary="获取稍后阅读列表")
async def list_queue(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, alias="pageSize", ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * pageSize
    rows = await get_queue(db, user_id=current_user.id, skip=skip, limit=pageSize)
    total = await get_queue_count(db, user_id=current_user.id)
    items = [
        {
            "id": news.id,
            "title": news.title,
            "title_zh": news.title_zh,
            "description": news.description,
            "image": news.image,
            "author": news.author,
            "source_platform": news.source_platform,
            "publishTime": news.publish_time,
            "categoryId": news.category_id,
            "views": news.views,
            "queueTime": queue_time,
        }
        for news, queue_time in rows
    ]
    return success_response({
        "list": items,
        "total": total,
        "hasMore": (skip + len(items)) < total,
    })


@router.delete("/clear", summary="清空稍后阅读")
async def clear_queue_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await clear_queue(db, user_id=current_user.id)
    return success_response(message=f"已清空 {count} 条记录")
