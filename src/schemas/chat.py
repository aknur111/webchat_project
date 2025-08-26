
from pydantic import BaseModel

class ChatCreate(BaseModel):
    name: str

class ChatOut(BaseModel):
    id: int
    name: str
    join_code: str

class JoinByCodeIn(BaseModel):
    code: str

