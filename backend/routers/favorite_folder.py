from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database_conf import get_db
from utils.security import get_current_user
from models.users import User
from schemas.favorite_folder import FolderCreate, FolderRename, FavoriteMove
from utils.response import success_response
from crud.favorite_folder import (
    list_folders,
    create_folder,
    rename_folder,
    delete_folder,
    count_favorites_in_folder,
    move_favorite,
)

router = APIRouter(prefix="/api/favorite/folder", tags=["favorite-folder"])


@router.get("/list")
async def list_folders_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    folders = await list_folders(db, user_id=current_user.id)
    items = [
        {
            "id": f.id,
            "name": f.name,
            "createdAt": f.created_at,
            "count": await count_favorites_in_folder(db, user_id=current_user.id, folder_id=f.id),
        }
        for f in folders
    ]
    unfiled_count = await count_favorites_in_folder(db, user_id=current_user.id, folder_id=None)
    return success_response({"list": items, "unfiledCount": unfiled_count})


@router.post("/create")
async def create_folder_endpoint(
    body: FolderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    folder = await create_folder(db, user_id=current_user.id, name=body.name.strip())
    return success_response({
        "id": folder.id,
        "name": folder.name,
        "createdAt": folder.created_at,
    }, "已创建")


@router.put("/{folder_id}/rename")
async def rename_folder_endpoint(
    folder_id: int,
    body: FolderRename,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    renamed = await rename_folder(db, user_id=current_user.id, folder_id=folder_id, name=body.name.strip())
    if not renamed:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    return success_response(message="已重命名")


@router.delete("/{folder_id}")
async def delete_folder_endpoint(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_folder(db, user_id=current_user.id, folder_id=folder_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    return success_response(message="已删除（文件夹内收藏已转为未分类）")


@router.post("/move")
async def move_favorite_endpoint(
    body: FavoriteMove,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    moved = await move_favorite(
        db, user_id=current_user.id,
        news_id=body.newsId, folder_id=body.folderId,
    )
    if not moved:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return success_response(message="已移动")
