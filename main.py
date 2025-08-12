from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from src.config.database import Base, engine
from src.endpoints.user import router as users_router
from src.endpoints.chat import router as chats_router
from src.endpoints.ws import router as ws_router

app = FastAPI(title="Chat (WS + DB) [sync]")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

HTML = """
<!doctype html><html><head><meta charset="utf-8"><title>Chat</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body class="container mt-4">
<h1>Webchat!</h1>
<div class="row g-2">
  <div class="col"><input id="chatId" class="form-control" placeholder="chat_id"></div>
  <div class="col"><input id="userId" class="form-control" placeholder="user_id"></div>
  <div class="col"><button class="btn btn-primary w-100" onclick="connectWS()">Connect</button></div>
</div>
<div class="mt-2"><b>Pinned:</b> <span id="pinned"></span></div>
<form class="mt-2" onsubmit="sendMsg(event)">
  <input id="msg" class="form-control" placeholder="message or /pin <text>">
  <button class="btn btn-outline-primary mt-2">Send</button>
</form>
<input id="q" class="form-control mt-2" placeholder="search..." oninput="filter()">
<ul id="log" class="list-group mt-2"></ul>
<script>
let ws;
function add(t){const li=document.createElement('li');li.className='list-group-item';li.textContent=t;li.dataset.raw=t.toLowerCase();document.getElementById('log').appendChild(li)}
function filter(){const f=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#log li').forEach(li=>li.style.display=li.dataset.raw.includes(f)?'':'none')}
function connectWS(){const c=document.getElementById('chatId').value.trim(), u=document.getElementById('userId').value.trim(); if(!c||!u){alert('set chat_id & user_id');return;} if(ws) ws.close(); ws=new WebSocket(`ws://localhost:8000/ws/${c}?user_id=${u}`); ws.onmessage=(e)=>{const m=e.data; if(m.startsWith('PINNED::')){document.getElementById('pinned').textContent=m.slice(8).trim();return;} add(m);};}
function sendMsg(e){e.preventDefault(); const i=document.getElementById('msg'); if(!ws||ws.readyState!==1){alert('connect first');return;} ws.send(i.value); i.value='';}
</script></body></html>
"""
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML)

app.include_router(users_router)
app.include_router(chats_router)
app.include_router(ws_router)
