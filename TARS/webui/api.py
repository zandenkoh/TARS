# Part of TARS integrated web UI – prepared for HTMX + Tailwind

import os
from pathlib import Path
from typing import Annotated

import json
from pathlib import Path
from typing import Annotated, AsyncGenerator

from fastapi import FastAPI, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from TARS.config.schema import Config
from TARS.config.paths import get_workspace_path
from TARS.bus.queue import MessageBus
from TARS.session.manager import SessionManager
from TARS.agent.loop import AgentLoop
from TARS.webui.utils import load_tars_config

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="TARS Web UI",
    description="Main Web Interface for TARS",
    version="0.5.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- TARS Core Initialization ---

class TARSState:
    """Singleton-like state for TARS core to avoid re-initializing on Every request."""
    _instance = None
    
    def __init__(self):
        from TARS.cli.commands import _make_provider, _load_runtime_config
        self.config = _load_runtime_config()
        self.workspace = get_workspace_path(self.config.workspace_path)
        self.bus = MessageBus(config=self.config)
        self.provider = _make_provider(self.config)
        self.sessions = SessionManager(self.workspace)
        self.agent = AgentLoop(
            bus=self.bus,
            provider=self.provider,
            workspace=self.workspace,
            model=self.config.agents.defaults.model,
            session_manager=self.sessions,
            # Basic defaults
        )

def get_tars() -> TARSState:
    if TARSState._instance is None:
        TARSState._instance = TARSState()
    return TARSState._instance

TARS = Annotated[TARSState, Depends(get_tars)]

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, tars: TARS):
    """Serve the main TARS chat interface."""
    model_name = tars.config.agents.defaults.model
    return templates.TemplateResponse(request, "index.html", {
        "model_name": model_name,
        "config": tars.config
    })

import uuid

@app.get("/api/sessions")
async def list_sessions(tars: TARS):
    """List all available chat sessions."""
    sessions = tars.sessions.list_sessions()
    # Filter for web sessions if needed, but for now show all
    return sessions

@app.get("/api/sessions/{session_id}", response_class=HTMLResponse)
async def get_session_history(request: Request, tars: TARS, session_id: str):
    """Get the message history for a specific session and render as HTMX fragments."""
    session = tars.sessions.get_or_create(session_id)
    # Filter out metadata and system messages for the UI
    messages = [m for m in session.messages if m.get("_type") != "metadata" and m.get("role") != "system"]
    
    # We want to render each message using the existing template
    return templates.TemplateResponse(request, "chat_history.html", {
        "messages": messages,
        "session_id": session_id
    })

@app.post("/api/chat")
async def chat(request: Request, tars: TARS, content: Annotated[str, Form()], session_id: str | None = Form(None)):
    """Handle chat messages and return the initial message frame + SSE link."""
    turn_id = uuid.uuid4().hex
    # Default to web:chat if no session_id provided, or generate a new one if it's "new"
    if not session_id or session_id == "new":
        session_id = f"web:{uuid.uuid4().hex[:8]}"
    
    # Ensure session exists and has a title if it's the first message
    session = tars.sessions.get_or_create(session_id)
    if not session.metadata.get("title"):
        session.metadata["title"] = content[:30] + "..." if len(content) > 30 else content
        tars.sessions.save(session)

    return templates.TemplateResponse(request, "chat_turn.html", {
        "user_message": content,
        "turn_id": turn_id,
        "session_id": session_id
    })

@app.get("/api/chat/stream")
async def chat_stream(request: Request, tars: TARS, content: str, turn_id: str, session_id: str = "web:chat"):
    """SSE stream for TARS agent response using HTMX SSE extension."""
    async def event_generator() -> AsyncGenerator[str, None]:
        first = True
        
        async def on_stream(delta: str):
            nonlocal first
            safe_delta = delta.replace("\n", "&#13;")
            
            data = safe_delta
            if first:
                first = False
                data += f"<span id='response-thinking-{turn_id}' hx-swap-oob='delete'></span>"
                
            yield f"event: message\ndata: {data}\n\n"

        # Signal the agent to process
        await tars.agent.process_direct(
            content,
            session_key=session_id,
            channel="web",
            chat_id="user",
            on_stream=on_stream
        )
        
        # Signal end of stream so HTMX closes connection
        yield "event: close\ndata: done\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "TARS Core Integrated"}

@app.get("/api/tasks/today")
async def get_tasks(tars: TARS):
    """Stub for daily tasks logic."""
    tasks_path = tars.workspace / "tasks"
    # Logic to find latest daily_*.json would go here
    return {"status": "ok", "path": str(tasks_path)}

@app.post("/api/voice")
async def voice_stub():
    return HTMLResponse("<span class='text-sky-400 text-xs italic'>Voice features coming soon...</span>")
