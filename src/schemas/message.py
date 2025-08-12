from pydantic import BaseModel

class MessageOut(BaseModel):
    id: int
    user: str | None
    content: str
    created_at: str
