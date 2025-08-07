
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-3">
    <h1>FastAPI WebSocket Chat</h1>
    <h2>Your ID: <span id="ws-id"></span></h2>

    <form onsubmit="sendMessage(event)">
        <input type="text" class="form-control" id="messageText" autocomplete="off" placeholder="Type your message or /pin ..." />
        <button class="btn btn-outline-primary mt-2">Send</button>
    </form>

    <div class="mt-3">
        <strong>Pinned:</strong> <span id="pinned"></span>
    </div>

    <input type="text" class="form-control mt-2" id="searchBox" placeholder="Search messages..." oninput="searchMessages()" />

    <ul id="messages" class="mt-4 list-group"></ul>
</div>

<script>
    let client_id = Date.now();
    document.getElementById("ws-id").textContent = client_id;

    let ws = new WebSocket("ws://localhost:8000/ws/" + client_id);

    ws.onmessage = function(event) {
        const message = event.data;

        if (message.startsWith("PINNED::")) {
            document.getElementById("pinned").textContent = message.slice(8).trim();
            return;
        }

        const li = document.createElement('li');
        li.className = "list-group-item";
        li.textContent = message;
        li.dataset.raw = message.toLowerCase();
        document.getElementById("messages").appendChild(li);
    };

    function sendMessage(event) {
        const input = document.getElementById("messageText");
        ws.send(input.value);
        input.value = '';
        event.preventDefault();
    }

    function searchMessages() {
        const filter = document.getElementById("searchBox").value.toLowerCase();
        const items = document.querySelectorAll("#messages li");

        items.forEach(item => {
            const text = item.dataset.raw;
            item.style.display = text.includes(filter) ? "" : "none";
        });
    }
</script>
</body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.messages: list[str] = []
        self.pinned_message: str | None = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    if manager.pinned_message:
        await websocket.send_text(f"PINNED::{manager.pinned_message}")

    try:
        while True:
            data = await websocket.receive_text()

            if data.startswith("/pin "):
                pin_candidate = data[len("/pin "):].strip()
                found = next((msg for msg in manager.messages if pin_candidate in msg), None)
                if found:
                    manager.pinned_message = pin_candidate
                    await manager.broadcast(f"PINNED::{pin_candidate}")
                else:
                    await manager.send_personal_message("Message not found in chat history to pin it (please write another message).", websocket)
                continue

            message = f"Client #{client_id} message is: {data}"
            manager.messages.append(message)

            await manager.send_personal_message(f"Your message: {data}", websocket)
            await manager.broadcast(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} has left the chat")
