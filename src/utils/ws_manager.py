from __future__ import annotations
from typing import DefaultDict, Set
from collections import defaultdict
from fastapi import WebSocket

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

    async def broadcast(self, chat_id: int, text: str) -> None:
        for ws in list(self.active_connections.get(chat_id, set())):
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(chat_id, ws)
