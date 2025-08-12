from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    id: int
    username: str
