from __future__ import annotations

import json

# Part of TARS integrated web UI – prepared for HTMX + Tailwind
import shutil
from pathlib import Path
from typing import Annotated, AsyncGenerator, List, Optional

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from TARS.config.schema import Config
from TARS.config.paths import get_workspace_path
from TARS.bus.queue import MessageBus
from TARS.session.manager import SessionManager
from TARS.agent.loop import AgentLoop

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
        from TARS.cli.commands import _load_runtime_config, _make_provider
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

    def refresh_config(self):
        """Reload configuration from disk."""
        from TARS.cli.commands import _load_runtime_config
        self.config = _load_runtime_config()
        # Update agent's config-based fields
        self.agent.model = self.config.agents.defaults.model
        # Workspace remains the same for now

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
    """Enhanced SSE stream for TARS agent response with tool hints."""
    async def event_generator() -> AsyncGenerator[str, None]:
        import asyncio
        queue = asyncio.Queue()
        first = True

        async def on_stream(delta: str):
            nonlocal first
            safe_delta = delta.replace("\n", "&#13;")
            data = safe_delta
            if first:
                first = False
                # Remove the "Processing..." pulse and start showing content
                data += f"<div id='response-thinking-{turn_id}' hx-swap-oob='delete'></div>"
            await queue.put(f"event: message\ndata: {data}\n\n")

        async def on_progress(text: str, tool_hint: bool = False):
            # Send tool hints as OOB updates to a status area
            if tool_hint:
                # Format: "web_search('...')" -> premium badge
                status_html = f"""<div id='response-status-{turn_id}' hx-swap-oob='innerHTML'>
                    <div class='flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-800 border border-white/5 animate-pulse'>
                        <div class='w-2 h-2 rounded-full bg-tars-primary'></div>
                        <span class='text-[10px] font-bold text-zinc-400 uppercase tracking-widest'>Executing: {text}</span>
                    </div>
                </div>"""
                await queue.put(f"event: message\ndata: {status_html}\n\n")

        # Start agent processing in the background
        process_task = asyncio.create_task(tars.agent.process_direct(
            content,
            session_key=session_id,
            channel="web",
            chat_id="user",
            on_stream=on_stream,
            on_progress=on_progress
        ))

        try:
            while not process_task.done() or not queue.empty():
                # If there's something in the queue, yield it immediately
                if not queue.empty():
                    yield await queue.get()
                    continue

                # Otherwise, wait for either the task to finish or something to arrive in the queue
                # We use a small sleep to avoid tight-looping while waiting for a task to finish
                # but it's better to use an event or just wait for the task.
                if process_task.done():
                    break

                await asyncio.sleep(0.05)

            # Ensure we drain the queue one last time
            while not queue.empty():
                yield await queue.get()

        except asyncio.CancelledError:
            process_task.cancel()
            raise

        # Final cleanup: remove status badge
        yield f"event: message\ndata: <div id='response-status-{turn_id}' hx-swap-oob='delete'></div>\n\n"
        yield "event: close\ndata: done\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "TARS Core Integrated"}

@app.get("/api/workspace", response_class=HTMLResponse)
async def list_workspace(request: Request, tars: TARS, path: str = "."):
    """List files in the workspace and render as HTMX fragments."""
    # Security: Ensure path is within workspace
    try:
        base_path = tars.workspace
        target_path = (base_path / path).resolve()
        if not target_path.is_relative_to(base_path.resolve()):
            return HTMLResponse("<div class='text-red-500'>Access Denied</div>")

        items = []
        for p in target_path.iterdir():
            if p.name.startswith('.'): continue # Hide hidden files
            items.append({
                "name": p.name,
                "is_dir": p.is_dir(),
                "size": f"{p.stat().st_size / 1024:.1f} KB" if p.is_file() else "-",
                "path": str(p.relative_to(base_path))
            })

        # Sort: directories first, then files
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        return templates.TemplateResponse(request, "components/file_explorer.html", {
            "items": items,
            "current_path": path,
            "parent_path": str(Path(path).parent) if path != "." else None
        })
    except Exception as e:
        return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")

@app.get("/api/config", response_class=HTMLResponse)
async def get_config_ui(request: Request, tars: TARS):
    """Render the configuration/settings dashboard."""
    # Convert to dict for easier iteration in template
    config_dict = tars.config.model_dump()
    return templates.TemplateResponse(request, "components/settings.html", {
        "config": config_dict,
        "workspace": str(tars.workspace)
    })

@app.get("/api/tasks/today", response_class=HTMLResponse)
async def get_tasks_ui(request: Request, tars: TARS):
    """Render the tasks and routine dashboard."""
    # Simplified logic to find daily task files
    tasks_dir = tars.workspace / "tasks"
    tasks = []
    if tasks_dir.exists():
        for p in sorted(tasks_dir.glob("daily_*.json"), reverse=True)[:5]:
            try:
                with open(p, "r") as f:
                    data = json.load(f)
                    tasks.append({"date": p.stem.replace("daily_", ""), "count": len(data.get("tasks", []))})
            except: continue

    return templates.TemplateResponse(request, "components/tasks.html", {
        "tasks": tasks,
        "tasks_path": str(tasks_dir)
    })

@app.get("/api/channels", response_class=HTMLResponse)
async def get_channels_ui(request: Request, tars: TARS):
    """Render the communication channels status dashboard."""
    channels = []
    if hasattr(tars.config, "channels"):
        # Pydantic v2 model_dump() includes extra fields allowed via extra="allow"
        all_channels_data = tars.config.channels.model_dump()

        # Filter out the internal config settings
        internal_keys = {"send_progress", "send_tool_hints"}

        for name, cfg in all_channels_data.items():
            if name in internal_keys:
                continue

            if isinstance(cfg, dict) and cfg.get("enabled"):
                # Mask sensitive IDs
                raw_id = cfg.get("appId") or cfg.get("botToken") or cfg.get("token") or "configured"
                masked_id = str(raw_id)[:10] + "..."

                channels.append({
                    "name": name,
                    "enabled": True,
                    "id": masked_id
                })
            else:
                channels.append({
                    "name": name,
                    "enabled": False,
                    "id": "N/A"
                })

    return templates.TemplateResponse(request, "components/channels.html", {
        "channels": channels
    })

@app.post("/api/channels/toggle")
async def toggle_channel(tars: TARS, name: str = Form(...)):
    """Toggle a communication channel's enabled status."""
    try:
        config_dict = tars.config.model_dump()
        channels = config_dict.get("channels", {})

        if name in channels:
            channels[name]["enabled"] = not channels[name].get("enabled", False)
        else:
            return JSONResponse({"status": "error", "message": f"Channel {name} not found"}, status_code=404)

        # Save updated config
        from TARS.config.loader import save_config
        from TARS.config.schema import Config
        new_config = Config.model_validate(config_dict)
        save_config(new_config)

        tars.refresh_config()
        return JSONResponse({"status": "success", "message": f"Channel {name} toggled", "enabled": channels[name]["enabled"]})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/workspace/move")
async def move_workspace_item(tars: TARS, src: str = Form(...), dst: str = Form(...)):
    """Move a file or folder within the workspace."""
    try:
        base = tars.workspace
        src_path = (base / src).resolve()
        dst_path = (base / dst).resolve()

        if not src_path.is_relative_to(base.resolve()) or \
           not dst_path.is_relative_to(base.resolve()):
            return JSONResponse({"status": "error", "message": "Access Denied"}, status_code=403)

        if dst_path.exists() and dst_path.is_dir():
            dst_path = (dst_path / src_path.name).resolve()
            if not dst_path.is_relative_to(base.resolve()):
                return JSONResponse({"status": "error", "message": "Access Denied: Invalid destination"}, status_code=403)

        shutil.move(str(src_path), str(dst_path))
        return JSONResponse({"status": "success", "message": f"Moved {src_path.name} to {dst}"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/workspace/upload")
async def upload_workspace_file(tars: TARS, path: str = Form("."), files: List[UploadFile] = File(...)):
    """Upload files to a specific path in the workspace."""
    try:
        base = tars.workspace
        target_dir = (base / path).resolve()
        if not target_dir.is_relative_to(base.resolve()):
            return JSONResponse({"status": "error", "message": "Access Denied"}, status_code=403)

        for file in files:
            # Prevent path traversal in filename
            file_path = (target_dir / file.filename).resolve()
            if not file_path.is_relative_to(base.resolve()):
                return JSONResponse({"status": "error", "message": "Access Denied: Invalid filename"}, status_code=403)

            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        return JSONResponse({"status": "success", "message": f"Uploaded {len(files)} files"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/tasks")
async def create_task(tars: TARS, content: str = Form(...), date: Optional[str] = Form(None)):
    """Manually create a task."""
    try:
        from datetime import datetime
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        tasks_dir = tars.workspace / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        file_path = tasks_dir / f"daily_{target_date}.json"
        tasks_data = {"tasks": [], "date": target_date}

        if file_path.exists():
            with open(file_path, "r") as f:
                tasks_data = json.load(f)

        tasks_data["tasks"].append({
            "id": uuid.uuid4().hex[:8],
            "content": content,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        })

        with open(file_path, "w") as f:
            json.dump(tasks_data, f, indent=2)

        return JSONResponse({"status": "success", "message": "Task created"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/config")
async def update_config(tars: TARS, config_json: str = Form(...)):
    """Save global configuration changes."""
    try:
        new_config = json.loads(config_json)
        tars.workspace / "tars_config.json" # Need to find the actual path
        # In TARS, config is usually in workspace or ~/.tars/config.json
        # The TARSState._load_runtime_config uses the paths.
        from TARS.config.paths import get_config_path
        path = get_config_path()

        with open(path, "w") as f:
            json.dump(new_config, f, indent=2)

        tars.refresh_config()
        return JSONResponse({"status": "success", "message": "Configuration updated and reloaded"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.post("/api/voice")
async def voice_stub():
    return HTMLResponse("<div class='p-8 glass rounded-3xl text-center'><span class='text-tars-primary font-heading animate-pulse'>Voice Recognition Engine initializing...</span></div>")
