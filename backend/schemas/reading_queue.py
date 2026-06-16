from pydantic import BaseModel


class QueueAdd(BaseModel):
    newsId: int
