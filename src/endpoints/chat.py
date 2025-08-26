from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.models.chat import Chat
from src.models.chat_member import ChatMember
from src.models.message import Message
from src.models.user import User
from src.schemas.chat import ChatCreate, ChatOut
from src.schemas.message import MessageOut
from src.utils.dependencies import get_current_user
from src.utils.helpers import generate_join_code
from src.schemas.chat import JoinByCodeIn

router = APIRouter(prefix="/chats", tags=["chats"])


# @router.post("", response_model=ChatOut, status_code=201)
# def create_chat(
#     payload: ChatCreate,
#     db: Session = Depends(get_db),
#     me: User = Depends(get_current_user),
# ):
#     code = generate_join_code()
#     while db.scalar(select(Chat).where(Chat.join_code == code)):
#         code = generate_join_code()
#
#     chat = Chat(name=payload.name, join_code=code)
#     db.add(chat)
#     db.commit()
#     db.refresh(chat)
#
#     db.add(ChatMember(chat_id=chat.id, user_id=me.id))
#     db.commit()
#
#     return ChatOut(id=chat.id, name=chat.name, join_code=chat.join_code)
@router.post("", response_model=ChatOut, status_code=201)
def create_chat(payload: ChatCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    code = generate_join_code()
    while db.scalar(select(Chat).where(Chat.join_code == code)):
        code = generate_join_code()

    chat = Chat(name=payload.name, join_code=code)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    db.add(ChatMember(chat_id=chat.id, user_id=me.id))
    db.commit()

    return ChatOut(id=chat.id, name=chat.name, join_code=chat.join_code)


@router.post("/{chat_id}/join")
def join_chat_by_id(
    chat_id: int,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")

    exists = db.scalar(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == me.id,
        )
    )
    if not exists:
        db.add(ChatMember(chat_id=chat_id, user_id=me.id))
        db.commit()
    return {"ok": True, "chat_id": chat_id}



@router.post("/join-by-code")
def join_by_code(
    data: JoinByCodeIn,
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    code = (data.code or "").strip().upper()
    chat = db.scalar(select(Chat).where(Chat.join_code == code))
    if not chat:
        raise HTTPException(404, "Invalid invite code")

    exists = db.scalar(
        select(ChatMember).where(
            ChatMember.chat_id == chat.id,
            ChatMember.user_id == me.id,
        )
    )
    if not exists:
        db.add(ChatMember(chat_id=chat.id, user_id=me.id))
        db.commit()

    return {"ok": True, "chat_id": chat.id, "name": chat.name}


@router.get("/{chat_id}/messages", response_model=list[MessageOut])
def get_messages(
    chat_id: int,
    q: str | None = Query(None, description="optional search substring"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    is_member = db.scalar(
        select(ChatMember).where(
            ChatMember.chat_id == chat_id,
            ChatMember.user_id == me.id,
        )
    )
    if not is_member:
        raise HTTPException(403, "Forbidden")

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
            created_at=m.created_at.isoformat(),
        )
        for m, u in rows
    ]

@router.get("", response_model=list[ChatOut])
def my_chats(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    rows = (
        db.query(Chat)
        .join(ChatMember, ChatMember.chat_id == Chat.id)
        .filter(ChatMember.user_id == me.id)
        .all()
    )
    return [ChatOut.model_validate(r) for r in rows]
