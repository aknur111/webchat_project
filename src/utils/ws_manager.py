from __future__ import annotations
from typing import Dict, Set, DefaultDict
from collections import defaultdict

from fastapi import WebSocket
from sqlalchemy.orm import Session

from src.models.message import Message
from src.models.user import User
from src.models.chat import Chat


class WSManager:

    def __init__(self) -> None:
        self.active_connections: DefaultDict[int, Set[WebSocket]] = defaultdict(set)

    async def connect(self, chat_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[chat_id].add(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket) -> None:
        conns = self.active_connections.get(chat_id)
        if not conns:
            return
        conns.discard(websocket)
        if not conns:
            self.active_connections.pop(chat_id, None)

    async def send_personal(self, websocket: WebSocket, text: str) -> None:
        await websocket.send_text(text)

    async def broadcast(self, chat_id: int, text: str) -> None:
        for ws in list(self.active_connections.get(chat_id, set())):
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(chat_id, ws)

    def save_message(self, db: Session, *, chat_id: int, user_id: int | None, content: str) -> Message:
        msg = Message(chat_id=chat_id, user_id=user_id, content=content, is_system=False)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
