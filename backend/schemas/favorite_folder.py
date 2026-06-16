from pydantic import BaseModel, Field


class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class FolderRename(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class FavoriteMove(BaseModel):
    newsId: int
    folderId: int | None = None
