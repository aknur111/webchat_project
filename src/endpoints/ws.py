from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.config.database import get_db
from src.models.chat import Chat
from src.models.user import User
from src.models.message import Message
from src.utils.ws_manager import WSManager

router = APIRouter(tags=["ws"])
manager = WSManager()

@router.websocket("/ws/{chat_id}")
async def ws_chat(ws: WebSocket, chat_id: int, user_id: int, db: Session = Depends(get_db)):
    chat = db.get(Chat, chat_id)
    user = db.get(User, user_id)
    if not chat or not user:
        await ws.close(code=4404)
        return

    await manager.connect(chat_id, ws)

    if chat.pinned_message_id:
        pinned = db.get(Message, chat.pinned_message_id)
        if pinned:
            await ws.send_text(f"PINNED::{pinned.content}")

    hist = db.execute(
        select(Message, User.username)
        .join(User, User.id == Message.user_id, isouter=True)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .limit(50)
    ).all()
    for m, u in hist:
        await ws.send_text(f"{(u or 'anonymous')}: {m.content}")

    try:
        while True:
            text_in = await ws.receive_text()

            if text_in.startswith("/pin "):
                needle = text_in[5:].strip()
                found = db.scalar(
                    select(Message).where(
                        Message.chat_id == chat_id,
                        Message.content.ilike(f"%{needle}%")
                    ).order_by(Message.created_at.asc())
                )
                if not found:
                    await ws.send_text("System: message not found in this chat")
                    continue

                chat.pinned_message_id = found.id
                db.commit()
                await manager.broadcast(chat_id, f"PINNED::{found.content}")
                continue

            msg = Message(chat_id=chat_id, user_id=user.id, content=text_in)
            db.add(msg)
            db.commit()
            db.refresh(msg)

            await manager.broadcast(chat_id, f"{user.username}: {msg.content}")

    except WebSocketDisconnect:
        manager.disconnect(chat_id, ws)
        await manager.broadcast(chat_id, f"System: {user.username} left the chat")
