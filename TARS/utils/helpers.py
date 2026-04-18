"""Utility functions for TARS."""

import base64
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import tiktoken

_TIKTOKEN_ENC = None


def _get_tiktoken_encoding():
    """Lazily load and cache tiktoken encoding."""
    global _TIKTOKEN_ENC
    if _TIKTOKEN_ENC is None:
        _TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")
    return _TIKTOKEN_ENC


def strip_think(text: str) -> str:
    """Remove <think>…</think> blocks and any unclosed trailing <think> tag."""
    if "<think>" not in text:
        return text.strip()

    parts: list[str] = []
    append = parts.append
    start = 0
    while True:
        start_idx = text.find("<think>", start)
        if start_idx == -1:
            append(text[start:])
            break

        append(text[start:start_idx])
        end_idx = text.find("</think>", start_idx + 7)
        if end_idx == -1:
            # Unclosed trailing <think>
            break
        start = end_idx + 8

    return "".join(parts).strip()


def detect_image_mime(data: bytes) -> str | None:
    """Detect image MIME type from magic bytes, ignoring file extension."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def build_image_content_blocks(
    raw: bytes, mime: str, path: str, label: str
) -> list[dict[str, Any]]:
    """Build native image blocks plus a short text label."""
    b64 = base64.b64encode(raw).decode()
    return [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"},
            "_meta": {"path": path},
        },
        {"type": "text", "text": label},
    ]


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamp() -> str:
    """Current ISO timestamp."""
    return datetime.now().isoformat()


def current_time_str(timezone: str | None = None) -> str:
    """Human-readable current time with weekday and UTC offset.

    When *timezone* is a valid IANA name (e.g. ``"Asia/Shanghai"``), the time
    is converted to that zone.  Otherwise falls back to the host local time.
    """
    from zoneinfo import ZoneInfo

    try:
        tz = ZoneInfo(timezone) if timezone else None
    except (KeyError, Exception):
        tz = None

    now = datetime.now(tz=tz) if tz else datetime.now().astimezone()
    offset = now.strftime("%z")
    offset_fmt = f"{offset[:3]}:{offset[3:]}" if len(offset) == 5 else offset
    tz_name = timezone or (time.strftime("%Z") or "UTC")
    return f"{now.strftime('%Y-%m-%d %H:%M (%A)')} ({tz_name}, UTC{offset_fmt})"


_UNSAFE_CHARS = re.compile(r'[<>:"/\\|?*]')


def safe_filename(name: str) -> str:
    """Replace unsafe path characters with underscores."""
    return _UNSAFE_CHARS.sub("_", name).strip()


def split_message(content: str, max_len: int = 2000) -> list[str]:
    """
    Split content into chunks within max_len, preferring line breaks.

    Args:
        content: The text content to split.
        max_len: Maximum length per chunk (default 2000 for Discord compatibility).

    Returns:
        List of message chunks, each within max_len.
    """
    if not content:
        return []
    if len(content) <= max_len:
        return [content]
    chunks: list[str] = []
    start = 0
    total_len = len(content)
    while start < total_len:
        if total_len - start <= max_len:
            chunks.append(content[start:])
            break

        cut_end = start + max_len
        # Try to break at newline first, then space, then hard break
        pos = content.rfind("\n", start, cut_end)
        if pos <= start:
            pos = content.rfind(" ", start, cut_end)
        if pos <= start:
            pos = cut_end

        chunks.append(content[start:pos])

        start = pos
        while start < total_len and content[start].isspace():
            start += 1

    return chunks


def build_assistant_message(
    content: str | None,
    tool_calls: list[dict[str, Any]] | None = None,
    reasoning_content: str | None = None,
    thinking_blocks: list[dict] | None = None,
) -> dict[str, Any]:
    """Build a provider-safe assistant message with optional reasoning fields."""
    msg: dict[str, Any] = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    if reasoning_content is not None:
        msg["reasoning_content"] = reasoning_content
    if thinking_blocks:
        msg["thinking_blocks"] = thinking_blocks
    return msg


def estimate_prompt_tokens(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
) -> int:
    """Estimate prompt tokens with tiktoken.

    Counts all fields that providers send to the LLM: content, tool_calls,
    reasoning_content, tool_call_id, name, plus per-message framing overhead.
    """
    try:
        enc = _get_tiktoken_encoding()

        # Fast path
        if not tools:
            try:
                fast_parts = []
                append_fast = fast_parts.append
                for m in messages:
                    if len(m) != 2:
                        fast_parts = None
                        break
                    content = m.get("content")
                    if type(content) is not str:
                        fast_parts = None
                        break
                    append_fast(content)
                if fast_parts is not None:
                    return len(enc.encode("\n".join(fast_parts))) + len(messages) * 4
            except Exception:
                pass

        parts: list[str] = []
        append = parts.append
        dumps = json.dumps
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, str):
                append(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        txt = part.get("text", "")
                        if txt:
                            append(txt)

            tc = msg.get("tool_calls")
            if tc:
                append(dumps(tc, ensure_ascii=False))

            rc = msg.get("reasoning_content")
            if isinstance(rc, str) and rc:
                append(rc)

            for key in ("name", "tool_call_id"):
                value = msg.get(key)
                if isinstance(value, str) and value:
                    append(value)

        if tools:
            append(dumps(tools, ensure_ascii=False))

        per_message_overhead = len(messages) * 4
        return len(enc.encode("\n".join(parts))) + per_message_overhead
    except Exception:
        return 0


def estimate_message_tokens(message: dict[str, Any]) -> int:
    """Estimate prompt tokens contributed by one persisted message."""
    try:
        # Fast path for simple messages (e.g. role + content string)
        if len(message) == 2:
            content = message.get("content")
            if type(content) is str:
                if not content:
                    return 4
                enc = _get_tiktoken_encoding()
                return max(4, len(enc.encode(content)) + 4)
    except Exception:
        pass

    content = message.get("content")
    parts: list[str] = []
    if isinstance(content, str):
        parts.append(content)
    elif isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text = part.get("text", "")
                if text:
                    parts.append(text)
            else:
                parts.append(json.dumps(part, ensure_ascii=False))
    elif content is not None:
        parts.append(json.dumps(content, ensure_ascii=False))

    for key in ("name", "tool_call_id"):
        value = message.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    if message.get("tool_calls"):
        parts.append(json.dumps(message["tool_calls"], ensure_ascii=False))

    rc = message.get("reasoning_content")
    if isinstance(rc, str) and rc:
        parts.append(rc)

    payload = "\n".join(parts)
    if not payload:
        return 4
    try:
        enc = _get_tiktoken_encoding()
        return max(4, len(enc.encode(payload)) + 4)
    except Exception:
        return max(4, len(payload) // 4 + 4)


def estimate_prompt_tokens_chain(
    provider: Any,
    model: str | None,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
) -> tuple[int, str]:
    """Estimate prompt tokens via provider counter first, then tiktoken fallback."""
    provider_counter = getattr(provider, "estimate_prompt_tokens", None)
    if callable(provider_counter):
        try:
            tokens, source = provider_counter(messages, tools, model)
            if isinstance(tokens, (int, float)) and tokens > 0:
                return int(tokens), str(source or "provider_counter")
        except Exception:
            pass

    estimated = estimate_prompt_tokens(messages, tools)
    if estimated > 0:
        return int(estimated), "tiktoken"
    return 0, "none"


def build_status_content(
    *,
    version: str,
    model: str,
    start_time: float,
    last_usage: dict[str, int],
    context_window_tokens: int,
    session_msg_count: int,
    context_tokens_estimate: int,
) -> str:
    """Build a human-readable runtime status snapshot."""
    uptime_s = int(time.time() - start_time)
    uptime = (
        f"{uptime_s // 3600}h {(uptime_s % 3600) // 60}m"
        if uptime_s >= 3600
        else f"{uptime_s // 60}m {uptime_s % 60}s"
    )
    last_in = last_usage.get("prompt_tokens", 0)
    last_out = last_usage.get("completion_tokens", 0)
    ctx_total = max(context_window_tokens, 0)
    ctx_pct = int((context_tokens_estimate / ctx_total) * 100) if ctx_total > 0 else 0
    ctx_used_str = (
        f"{context_tokens_estimate // 1000}k"
        if context_tokens_estimate >= 1000
        else str(context_tokens_estimate)
    )
    ctx_total_str = f"{ctx_total // 1024}k" if ctx_total > 0 else "n/a"
    return "\n".join(
        [
            f"\U0001f408 TARS v{version}",
            f"\U0001f9e0 Model: {model}",
            f"\U0001f4ca Tokens: {last_in} in / {last_out} out",
            f"\U0001f4da Context: {ctx_used_str}/{ctx_total_str} ({ctx_pct}%)",
            f"\U0001f4ac Session: {session_msg_count} messages",
            f"\u23f1 Uptime: {uptime}",
        ]
    )


def sync_workspace_templates(workspace: Path, silent: bool = False) -> list[str]:
    """Sync bundled templates to workspace. Only creates missing files."""
    from importlib.resources import files as pkg_files

    try:
        tpl = pkg_files("TARS") / "templates"
    except Exception:
        return []
    if not tpl.is_dir():
        return []

    added: list[str] = []

    def _write(src, dest: Path):
        if dest.exists():
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8") if src else "", encoding="utf-8")
        added.append(str(dest.relative_to(workspace)))

    for item in tpl.iterdir():
        if item.name.endswith(".md") and not item.name.startswith("."):
            _write(item, workspace / item.name)
    _write(tpl / "memory" / "MEMORY.md", workspace / "memory" / "MEMORY.md")
    _write(None, workspace / "memory" / "HISTORY.md")
    (workspace / "skills").mkdir(exist_ok=True)

    if added and not silent:
        from rich.console import Console

        for name in added:
            Console().print(f"  [dim]Created {name}[/dim]")
    return added
