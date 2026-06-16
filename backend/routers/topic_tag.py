from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_conf import get_db
from crud import topic_tag as crud
from schemas.topic_tag import TagOut
from typing import List

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=List[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await crud.list_tags(db)


@router.get("/news/{news_id}", response_model=List[TagOut])
async def news_tags(news_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_tags_for_news(db, news_id)
