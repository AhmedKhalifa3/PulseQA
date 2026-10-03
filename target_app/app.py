"""
PulseChat: High-performance target web application & API for PulseQA.
Features:
- Token-based & Session Authentication
- Real-time WebSocket multi-room chat
- Controlled CPU & Memory stress endpoints for resource profiling verification
"""

import os
import time

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="PulseChat Application", version="2.4.0")

# Mount static and templates
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# In-memory storage
VALID_USERS = {
    "alex": "pulse123",
    "sarah": "pulse123",
    "qa_automator": "securepass",
    "admin": "adminpass"
}

ACTIVE_TOKENS: dict[str, str] = {
    "test-token-alex": "alex",
    "test-token-qa": "qa_automator"
}

MESSAGES: dict[str, list[dict]] = {
    "general": [
        {"id": 1, "user": "System", "text": "Welcome to PulseChat #general room!", "timestamp": "12:00"}
    ],
    "qa-testing": [
        {"id": 2, "user": "System", "text": "Automation test channel ready.", "timestamp": "12:01"}
    ]
}

# Retained memory buffer for memory leak simulation
LEAK_BUFFER: list[bytes] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {
            "general": set(),
            "qa-testing": set()
        }

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)

    async def broadcast(self, room: str, message: dict):
        if room in self.active_connections:
            for connection in list(self.active_connections[room]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(room, connection)

manager = ConnectionManager()

# --- Request / Response Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class MessageRequest(BaseModel):
    room: str
    text: str

class StressRequest(BaseModel):
    duration_sec: float = 1.0
    intensity: float = 0.8
    memory_mb: int = 20

# --- Frontend Routes ---
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# --- REST API Endpoints ---
@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if req.username in VALID_USERS and VALID_USERS[req.username] == req.password:
        token = f"token-{req.username}-{int(time.time())}"
        ACTIVE_TOKENS[token] = req.username
        return {"status": "success", "token": token, "username": req.username}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/auth/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token in ACTIVE_TOKENS:
        del ACTIVE_TOKENS[token]
    return {"status": "logged_out"}

@app.get("/api/chat/rooms")
async def get_rooms():
    return {"rooms": list(MESSAGES.keys())}

@app.get("/api/chat/messages/{room}")
async def get_messages(room: str):
    if room not in MESSAGES:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"room": room, "messages": MESSAGES[room]}

@app.post("/api/chat/messages")
async def post_message(req: MessageRequest, request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    username = ACTIVE_TOKENS.get(token, "anonymous")

    if req.room not in MESSAGES:
        MESSAGES[req.room] = []

    msg_id = len(MESSAGES[req.room]) + 1
    new_msg = {
        "id": msg_id,
        "user": username,
        "text": req.text,
        "timestamp": time.strftime("%H:%M:%S")
    }
    MESSAGES[req.room].append(new_msg)
    await manager.broadcast(req.room, new_msg)
    return {"status": "sent", "message": new_msg}

# --- System & Stress Endpoints (for Telemetry QA) ---
@app.get("/api/system/health")
async def system_health():
    import psutil
    process = psutil.Process(os.getpid())
    return {
        "status": "healthy",
        "cpu_percent": process.cpu_percent(interval=None),
        "memory_rss_mb": round(process.memory_info().rss / (1024 * 1024), 2),
        "threads": process.num_threads(),
        "timestamp": time.time()
    }

@app.post("/api/system/stress/cpu")
async def stress_cpu(req: StressRequest):
    """Generates controlled CPU burn to test telemetry alert triggers."""
    start_time = time.time()
    count = 0
    while time.time() - start_time < min(req.duration_sec, 3.0):
        count += 1
        _ = [x ** 2 for x in range(1000)]
    return {"status": "cpu_stressed", "duration_sec": req.duration_sec, "iterations": count}

@app.post("/api/system/stress/memory")
async def stress_memory(req: StressRequest):
    """Allocates controlled memory buffer to test leak detection."""
    mb = min(req.memory_mb, 100)
    chunk = b"X" * (mb * 1024 * 1024)
    LEAK_BUFFER.append(chunk)
    return {"status": "memory_allocated", "allocated_mb": mb, "total_chunks": len(LEAK_BUFFER)}

@app.post("/api/system/stress/memory/reset")
async def reset_memory():
    LEAK_BUFFER.clear()
    import gc
    gc.collect()
    return {"status": "memory_reset", "current_chunks": len(LEAK_BUFFER)}

# --- WebSocket Channel ---
@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(room, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            user = data.get("user", "Guest")
            text = data.get("text", "")

            if room not in MESSAGES:
                MESSAGES[room] = []

            msg = {
                "id": len(MESSAGES[room]) + 1,
                "user": user,
                "text": text,
                "timestamp": time.strftime("%H:%M:%S")
            }
            MESSAGES[room].append(msg)
            await manager.broadcast(room, msg)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
