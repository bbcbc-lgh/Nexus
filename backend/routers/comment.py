from fastapi import APIRouter, Depends, Query, Path
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from config.database_conf import get_db
from utils.response import success_response
from utils.security import get_current_user

router = APIRouter(prefix="/api/comments", tags=["comments"])


class CommentIn(BaseModel):
    news_id: int
    content: str
    parent_id: int | None = None

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('评论不能为空')
        if len(v) > 1000:
            raise ValueError('评论不能超过1000字')
        return v


@router.get("", summary="获取评论列表")
async def list_comments(
    news_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="pageSize", le=50),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    rows = await db.execute(text("""
        SELECT c.id, c.parent_id, c.content, c.created_at,
               u.id AS uid, u.nickname, u.avatar
        FROM comment c
        JOIN user u ON u.id = c.user_id
        WHERE c.news_id = :nid
        ORDER BY c.created_at ASC
        LIMIT :lim OFFSET :off
    """), {"nid": news_id, "lim": page_size, "off": offset})
    total_row = await db.execute(text(
        "SELECT COUNT(*) FROM comment WHERE news_id = :nid"
    ), {"nid": news_id})
    total = total_row.scalar() or 0
    items = [
        {
            "id": r[0],
            "parentId": r[1],
            "content": r[2],
            "createdAt": str(r[3]),
            "user": {"id": r[4], "nickname": r[5] or "匿名", "avatar": r[6]},
        }
        for r in rows.all()
    ]
    return success_response({"list": items, "total": total, "hasMore": (offset + len(items)) < total})


@router.post("", summary="发布评论")
async def create_comment(
    body: CommentIn,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        INSERT INTO comment (news_id, user_id, parent_id, content)
        VALUES (:nid, :uid, :pid, :content)
    """), {"nid": body.news_id, "uid": current_user.id, "pid": body.parent_id, "content": body.content})
    comment_id = result.lastrowid
    await db.execute(text(
        "UPDATE news SET comment_count = comment_count + 1 WHERE id = :nid"
    ), {"nid": body.news_id})
    await db.commit()
    # 返回完整评论对象（含用户信息）
    row = await db.execute(text("""
        SELECT c.id, c.parent_id, c.content, c.created_at,
               u.id AS uid, u.nickname, u.avatar
        FROM comment c JOIN user u ON u.id = c.user_id
        WHERE c.id = :cid
    """), {"cid": comment_id})
    r = row.fetchone()
    return success_response({
        "id": r[0], "parentId": r[1], "content": r[2], "createdAt": str(r[3]),
        "user": {"id": r[4], "nickname": r[5] or "匿名", "avatar": r[6]},
    }, "评论成功")


@router.delete("/{comment_id}", summary="删除评论")
async def delete_comment(
    comment_id: int = Path(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text(
        "SELECT user_id, news_id FROM comment WHERE id = :cid"
    ), {"cid": comment_id})
    r = row.fetchone()
    if not r:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="评论不存在")
    if r[0] != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="无权删除")
    await db.execute(text("DELETE FROM comment WHERE id = :cid"), {"cid": comment_id})
    await db.execute(text(
        "UPDATE news SET comment_count = GREATEST(0, comment_count - 1) WHERE id = :nid"
    ), {"nid": r[1]})
    await db.commit()
    return success_response(None, "已删除")
