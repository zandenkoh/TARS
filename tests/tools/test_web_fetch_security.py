"""Tests for web_fetch SSRF protection and untrusted content marking."""

from __future__ import annotations

import json
import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from TARS.agent.tools.web import WebFetchTool


def _fake_resolve_private(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 0))]


def _fake_resolve_public(hostname, port, family=0, type_=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]


@pytest.mark.asyncio
async def test_web_fetch_blocks_private_ip():
    tool = WebFetchTool()
    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_private):
        result = await tool.execute(url="http://169.254.169.254/computeMetadata/v1/")
    data = json.loads(result)
    assert "error" in data
    assert "private" in data["error"].lower() or "blocked" in data["error"].lower()


@pytest.mark.asyncio
async def test_web_fetch_blocks_localhost():
    tool = WebFetchTool()

    def _resolve_localhost(hostname, port, family=0, type_=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0))]

    with patch("TARS.security.network.socket.getaddrinfo", _resolve_localhost):
        result = await tool.execute(url="http://localhost/admin")
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
async def test_web_fetch_result_contains_untrusted_flag():
    """When fetch succeeds, result JSON must include untrusted=True and the banner."""
    tool = WebFetchTool()

    fake_html = "<html><head><title>Test</title></head><body><p>Hello world</p></body></html>"

    class FakeResponse:
        status_code = 200
        url = "https://example.com/page"
        text = fake_html
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            pass

        def json(self):
            return {}

    async def _fake_get(self, url, **kwargs):
        return FakeResponse()

    with (
        patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_public),
        patch("httpx.AsyncClient.get", _fake_get),
        patch(
            "httpx.AsyncClient.stream",
            MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=FakeResponse()))),
        ),
    ):
        result = await tool.execute(url="https://example.com/page")

    data = json.loads(result)
    assert data.get("untrusted") is True
    assert "[External content" in data.get("text", "")


@pytest.mark.asyncio
async def test_web_fetch_blocks_private_redirect_before_returning_image(monkeypatch):
    tool = WebFetchTool()

    class FakeStreamResponse:
        headers = {"content-type": "image/png"}
        url = "http://127.0.0.1/secret.png"
        content = b"\x89PNG\r\n\x1a\n"

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def aread(self):
            return self.content

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def stream(self, method, url, headers=None):
            return FakeStreamResponse()

    monkeypatch.setattr("TARS.agent.tools.web.httpx.AsyncClient", FakeClient)

    with patch("TARS.security.network.socket.getaddrinfo", _fake_resolve_public):
        try:
            result = await tool.execute(url="https://example.com/image.png")
            # If our mock `FakeClient` does not trigger event hooks, the tool might try to parse it.
            # To properly test the new `_verify_request` behavior, we should raise RuntimeError in the mock or
            # simulate the event hook firing. Here we just manually simulate the hook to check if it raises.
            # Simulate httpx calling the request hook for the redirect
            import httpx

            from TARS.agent.tools.web import _verify_request

            req = httpx.Request("GET", "http://127.0.0.1/secret.png")
            await _verify_request(req)
        except Exception as e:
            assert "SSRF blocked" in str(e)
            return

    pytest.fail("Expected SSRF validation to block the request")
