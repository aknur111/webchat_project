from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

UserCreate = UserRegister

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
