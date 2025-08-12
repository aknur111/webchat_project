from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.config.database import get_db
from src.models.chat import Chat
from src.models.chat_member import ChatMember
from src.models.user import User
from src.models.message import Message
from src.schemas.chat import ChatCreate, ChatOut
from src.schemas.message import MessageOut

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("", response_model=ChatOut)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Chat).where(Chat.name == payload.name))
    if exists:
        raise HTTPException(400, "Chat already exists")
    chat = Chat(name=payload.name)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return ChatOut(id=chat.id, name=chat.name)

@router.post("/{chat_id}/join")
def join_chat(chat_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    chat = db.get(Chat, chat_id)
    user = db.get(User, user_id)
    if not chat or not user:
        raise HTTPException(404, "Chat or user not found")

    exists = db.scalar(select(ChatMember).where(
        ChatMember.chat_id == chat_id, ChatMember.user_id == user_id
    ))
    if not exists:
        db.add(ChatMember(chat_id=chat_id, user_id=user_id))
        db.commit()
    return {"ok": True}

@router.get("/{chat_id}/messages", response_model=list[MessageOut])
def search_messages(chat_id: int, q: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    stmt = (
        select(Message, User.username)
        .join(User, User.id == Message.user_id, isouter=True)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    if q:
        stmt = stmt.where(Message.content.ilike(f"%{q}%"))

    rows = db.execute(stmt).all()
    return [
        MessageOut(
            id=m.id,
            user=u,
            content=m.content,
            created_at=m.created_at.isoformat()
        ) for m, u in rows
    ]
