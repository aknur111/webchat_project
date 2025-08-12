from pydantic import BaseModel

class ChatCreate(BaseModel):
    name: str

class ChatOut(BaseModel):
    id: int
    name: str
