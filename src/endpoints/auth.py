from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.config.database import get_db
from src.models.user import User
from src.models.chat_member import ChatMember
from src.models.chat import Chat
from src.schemas.user import UserRegister, UserLogin, UserOut
from src.utils.helpers import hash_password, verify_password
from src.utils.jwt import create_token
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
COOKIE_NAME = "access_token"

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.username == data.username))
    if exists:
        raise HTTPException(409, "Username already taken")
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=UserOut)
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(str(user.id))
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60*60*24*7,
        path="/",
    )
    return user

@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")

# @router.get("/me")
# def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     rows = (
#         db.query(Chat)
#         .join(ChatMember, ChatMember.chat_id == Chat.id)
#         .filter(ChatMember.user_id == user.id)
#         .order_by(Chat.name.asc())
#         .all()
#     )
#     return {
#         "id": user.id,
#         "username": user.username,
#         "chats": [{"id": c.id, "name": c.name} for c in rows],
#     }

@router.get("/me")
def me(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    rows = (
        db.query(Chat)
        .join(ChatMember, ChatMember.chat_id == Chat.id)
        .filter(ChatMember.user_id == me.id)
        .all()
    )
    return {
        "id": me.id,
        "username": me.username,
        "chats": [{"id": c.id, "name": c.name, "join_code": c.join_code} for c in rows]
    }
