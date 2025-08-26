from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.config.database import get_db
from src.models.chat_member import ChatMember
from src.models.chat import Chat
from src.models.message import Message
from src.models.user import User
from src.utils.jwt import decode_token
from src.utils.ws_manager import WSManager
from src.utils.logger import logger

router = APIRouter(tags=["ws"])
manager = WSManager()
COOKIE_NAME = "access_token"

@router.websocket("/ws/{chat_id}")
async def ws_endpoint(websocket: WebSocket, chat_id: int, db: Session = Depends(get_db)):
    token = websocket.cookies.get(COOKIE_NAME) or websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401, reason="Missing token")
        return

    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=4401, reason="Invalid token"); return

    member = db.query(ChatMember).filter(
        ChatMember.chat_id == chat_id, ChatMember.user_id == user_id
    ).first()
    if not member:
        await websocket.close(code=4403, reason="Not a member of chat"); return

    await manager.connect(chat_id, websocket)

    await websocket.send_text(f"System: connected as user {user_id}")

    chat = db.get(Chat, chat_id)
    if chat and chat.pinned_message_id:
        pinned = db.get(Message, chat.pinned_message_id)
        if pinned:
            await websocket.send_text(f"PINNED::{pinned.content}")

    hist = db.execute(
        select(Message, User.username)
        .join(User, User.id == Message.user_id, isouter=True)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .limit(50)
    ).all()
    for m, u in hist:
        await websocket.send_text(f"{(u or 'anonymous')}: {m.content}")

    try:
        while True:
            text_in = await websocket.receive_text()
            logger.info(f"[WS] recv chat={chat_id} user={user_id} text={text_in!r}")

            if text_in.startswith("/pin "):
                needle = text_in[5:].strip()
                found = db.scalar(
                    select(Message).where(
                        Message.chat_id == chat_id,
                        Message.content.ilike(f"%{needle}%")
                    ).order_by(Message.created_at.asc())
                )
                if not found:
                    await websocket.send_text("System: message not found in this chat")
                    continue

                chat.pinned_message_id = found.id
                db.commit()
                await manager.broadcast(chat_id, f"PINNED::{found.content}")
                continue

            msg = Message(chat_id=chat_id, user_id=user_id, content=text_in)
            db.add(msg)
            db.commit()
            db.refresh(msg)

            username = db.get(User, user_id).username
            print(f"[WS] broadcast chat={chat_id} msg_id={msg.id}")
            await manager.broadcast(chat_id, f"{username}: {msg.content}")

    except WebSocketDisconnect:
        print(f"[WS] disconnect chat={chat_id} user={user_id}")
        manager.disconnect(chat_id, websocket)
