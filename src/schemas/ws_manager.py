from typing import Dict, Set
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.rooms: Dict[int, Set[WebSocket]] = {}

    async def connect(self, chat_id: int, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(chat_id, set()).add(ws)

    def disconnect(self, chat_id: int, ws: WebSocket):
        room = self.rooms.get(chat_id)
        if not room:
            return
        room.discard(ws)
        if not room:
            self.rooms.pop(chat_id, None)

    async def broadcast(self, chat_id: int, text: str):
        for ws in list(self.rooms.get(chat_id, [])):
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(chat_id, ws)
