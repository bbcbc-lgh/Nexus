from pydantic import BaseModel, Field


class FollowAuthorIn(BaseModel):
    author: str = Field(..., min_length=1, max_length=100)
