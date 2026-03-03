from pydantic import BaseModel


class Resource(BaseModel):
    name: str
    quantity: int
