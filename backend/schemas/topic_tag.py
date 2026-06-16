from pydantic import BaseModel


class TagOut(BaseModel):
    id:    int
    name:  str
    slug:  str
    color: str

    model_config = {"from_attributes": True}
