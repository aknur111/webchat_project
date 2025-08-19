from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from src.config.database import Base, engine
from src.endpoints.chat import router as chats_router
from src.endpoints.ws import router as ws_router
from src.endpoints.auth import router as auth_router

app = FastAPI(title="Chat (WS + DB) [sync]")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

HTML = """
<<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Webchat!</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container py-4">
  <h1 class="mb-3">Webchat!</h1>

  <div id="authBox" class="card p-3 mb-3">
    <h5 class="mb-3">Sign in</h5>
    <div class="row g-2">
      <div class="col-12 col-md"><input id="u" class="form-control" placeholder="username"></div>
      <div class="col-12 col-md"><input id="p" type="password" class="form-control" placeholder="password"></div>
      <div class="col-12 col-md-auto d-flex gap-2">
        <button class="btn btn-primary" onclick="login()">Login</button>
        <button class="btn btn-outline-secondary" onclick="register()">Register</button>
      </div>
    </div>
  </div>

  <div id="appBox" class="d-none">
    <div class="d-flex align-items-center gap-3 mb-3">
      <div class="fw-semibold">Hello, <span id="who"></span></div>
      <button class="btn btn-sm btn-outline-danger" onclick="logout()">Logout</button>
    </div>

    <div class="row g-2 align-items-center mb-2">
      <div class="col"><input id="newChatName" class="form-control" placeholder="New chat name"></div>
      <div class="col-auto">
        <button class="btn btn-success" onclick="createChat()">Create chat</button>
      </div>
    </div>

    <div class="row g-2 align-items-center mb-4">
      <div class="col"><input id="joinCode" class="form-control" placeholder="Enter invite code"></div>
      <div class="col-auto">
        <button class="btn btn-outline-primary" onclick="joinByCode()">Join by code</button>
      </div>
    </div>

    <div class="mb-3">
      <label class="form-label">My chats</label>
      <div id="chatList" class="list-group"></div>
    </div>

    <div id="currentChat" class="mb-2 d-none">
      <div class="mb-1"><b>Status:</b> <span id="status">disconnected</span></div>
      <div class="mb-2"><b>Pinned:</b> <span id="pinned"></span></div>

      <form id="msgForm" onsubmit="sendMsg(event)" class="mb-2">
        <input id="msg" class="form-control" placeholder="message or /pin &lt;text&gt;">
        <button id="sendBtn" type="submit" class="btn btn-outline-primary mt-2" disabled>Send</button>
      </form>

      <div class="d-flex gap-2 mb-2">
        <input id="q" class="form-control" placeholder="search..." oninput="filter()">
        <button class="btn btn-outline-secondary" onclick="loadHistory()">History</button>
      </div>

      <ul id="log" class="list-group"></ul>
    </div>
  </div>

<script>
let ws = null;
let currentChatId = null;

function $(id){ return document.getElementById(id); }
function add(t){
  const li=document.createElement('li');
  li.className='list-group-item';
  li.textContent=t;
  li.dataset.raw=t.toLowerCase();
  $('log').appendChild(li);
}
function filter(){
  const f=$('q').value.toLowerCase();
  document.querySelectorAll('#log li')
    .forEach(li=>li.style.display=li.dataset.raw.includes(f)?'':'none');
}

async function register(){
  const r = await fetch('/auth/register',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:$('u').value.trim(), password:$('p').value})
  });
  if(!r.ok){ alert('Register failed'); return; }
  alert('Registered. Now login.');
}
async function login(){
  const r = await fetch('/auth/login',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({username:$('u').value.trim(), password:$('p').value})
  });
  if(!r.ok){ alert('Login failed'); return; }
  await initApp();
}
async function logout(){
  await fetch('/auth/logout',{method:'POST'});
  try{ ws?.close(); }catch{}
  ws = null; currentChatId = null;
  $('sendBtn').disabled = true;
  $('currentChat').classList.add('d-none');
  $('appBox').classList.add('d-none');
  $('authBox').classList.remove('d-none');
}

async function initApp(){
  const r = await fetch('/auth/me');
  if(!r.ok){
    $('authBox').classList.remove('d-none');
    $('appBox').classList.add('d-none');
    return;
  }
  const me = await r.json();
  $('who').textContent = me.username;
  $('authBox').classList.add('d-none');
  $('appBox').classList.remove('d-none');
  renderChats(me.chats || []);
  $('currentChat').classList.add('d-none');
}

function renderChats(chats){
  const box=$('chatList'); box.innerHTML='';
  if(chats.length===0){
    box.innerHTML='<div class="list-group-item">No chats yet</div>';
    return;
  }
  chats.forEach(c=>{
    const row=document.createElement('div');
    row.className='list-group-item d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2';

    const left=document.createElement('div');
    left.innerHTML = `<span class="fw-semibold">${c.name}</span>` + (c.join_code ? ` <span class="badge text-bg-light ms-2">code: ${c.join_code}</span>` : '');

    const right=document.createElement('div');
    right.className='d-flex gap-2';

    const btnJoin=document.createElement('button');
    btnJoin.className='btn btn-primary btn-sm';
    btnJoin.textContent='Join';
    btnJoin.onclick = ()=>joinAndConnect(c.id);

    const btnHistory=document.createElement('button');
    btnHistory.className='btn btn-outline-secondary btn-sm';
    btnHistory.textContent='History';
    btnHistory.onclick = ()=>{ currentChatId=c.id; $('log').innerHTML=''; $('pinned').textContent=''; loadHistory(); $('currentChat').classList.remove('d-none'); };

    right.append(btnHistory, btnJoin);
    row.append(left, right);
    box.appendChild(row);
  });
}

async function createChat(){
  const name=$('newChatName').value.trim();
  if(!name) return;
  const r = await fetch('/chats', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name})
  });
  if(!r.ok){ alert('Create failed'); return; }
  const chat = await r.json();
  alert(`Chat created.\\nInvite code: ${chat.join_code}`);
  $('newChatName').value='';
  await initApp();
}

async function joinByCode(){
  const code = $('joinCode').value.trim().toUpperCase();
  if(!code) return;
  const r = await fetch('/chats/join-by-code', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({code})
  });
  if(!r.ok){ alert('Invalid code'); return; }
  const data = await r.json();
  $('joinCode').value='';
  await initApp();
  await joinAndConnect(data.chat_id);
}

async function joinAndConnect(chatId){
  await fetch(`/chats/${chatId}/join`, { method:'POST' });
  connectWS(chatId);
}

function connectWS(chatId){
  try{ ws?.close(); }catch{}
  $('log').innerHTML=''; $('pinned').textContent='';
  $('status').textContent='connecting…';
  $('sendBtn').disabled = true;

  currentChatId = chatId;
  $('currentChat').classList.remove('d-none');

  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const url = `${proto}://${location.host}/ws/${encodeURIComponent(chatId)}`;
  ws = new WebSocket(url);

  ws.onopen = () => {
    console.log('[WS] open');
    $('status').textContent='connected';
    $('sendBtn').disabled = false;
    loadHistory();
  };
  ws.onmessage = (e) => {
    const m = e.data || '';
    if(m.startsWith('PINNED::')){
      $('pinned').textContent = m.slice(8).trim();
      return;
    }
    add(m);
  };
  ws.onerror = (e) => {
    console.error('[WS] error', e);
  };
  ws.onclose = (e) => {
    console.warn('[WS] close', e);
    const info = e && typeof e.code === 'number'
      ? `disconnected (code ${e.code}${e.reason? ', '+e.reason: ''})`
      : 'disconnected';
    $('status').textContent = info;
    $('sendBtn').disabled = true;
  };
}

function sendMsg(e){
  e.preventDefault();

  if(!ws){
    alert('Connect to a chat first'); return;
  }
  if(ws.readyState !== WebSocket.OPEN){
    alert('Socket not open (state '+ws.readyState+')'); return;
  }

  const v = $('msg').value.trim();
  if(!v) return;

  console.log('[WS] send:', v);
  try {
    ws.send(v);
    add('(you) ' + v);
    $('msg').value='';
  } catch (err) {
    console.error('[WS] send failed:', err);
    alert('Send failed: ' + (err?.message || err));
  }
}
</script>
</body>
</html>

"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(HTML)

app.include_router(chats_router)
app.include_router(ws_router)
app.include_router(auth_router)
