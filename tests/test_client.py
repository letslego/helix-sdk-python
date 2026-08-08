from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from helix_sdk import HelixClient, HelixError


def _response(payload: object, status: int = 200):
    body = json.dumps(payload).encode("utf-8")
    cm = MagicMock()
    cm.read.return_value = body
    cm.__enter__.return_value = cm
    cm.__exit__.return_value = False
    if status >= 400:
        import urllib.error

        raise urllib.error.HTTPError(
            "http://example.test/x",
            status,
            "err",
            hdrs=None,  # type: ignore[arg-type]
            fp=MagicMock(read=MagicMock(return_value=body)),
        )
    return cm


def test_chat_posts_sessions():
    client = HelixClient("http://127.0.0.1:8787/")
    with patch("helix_sdk.client.urllib.request.urlopen") as urlopen:
        urlopen.return_value = _response(
            {
                "sessionId": "s1",
                "reply": "hello",
                "usage": {
                    "promptTokens": 1,
                    "completionTokens": 1,
                    "totalTokens": 2,
                    "estimatedCostUsd": 0,
                },
                "toolCalls": [],
                "events": [],
            }
        )
        result = client.chat("Plan a trip", auto_approve=True)
        req = urlopen.call_args.args[0]
        assert req.full_url == "http://127.0.0.1:8787/helix/v1/sessions"
        assert req.get_method() == "POST"
        assert result.session_id == "s1"
        assert result.reply == "hello"


def test_agent_and_bearer():
    client = HelixClient("http://example.test", token="secret")
    with patch("helix_sdk.client.urllib.request.urlopen") as urlopen:
        urlopen.return_value = _response({"config": {"model": "mock/helix-demo"}})
        data = client.agent()
        req = urlopen.call_args.args[0]
        assert req.get_header("Authorization") == "Bearer secret"
        assert data["config"]["model"] == "mock/helix-demo"


def test_helix_error():
    client = HelixClient("http://example.test")
    with patch("helix_sdk.client.urllib.request.urlopen") as urlopen:
        urlopen.side_effect = lambda *a, **k: (_ for _ in ()).throw(
            __import__("urllib.error").error.HTTPError(
                "http://example.test/helix/v1/stack",
                404,
                "nf",
                hdrs=None,
                fp=MagicMock(read=MagicMock(return_value=b'{"error":"not_found"}')),
            )
        )
        with pytest.raises(HelixError) as exc:
            client.stack()
        assert exc.value.status == 404
        assert str(exc.value) == "not_found"


def test_resolve_approval_and_schedule():
    client = HelixClient("http://example.test")
    paths: list[str] = []

    def fake_urlopen(req, timeout=None):
        paths.append(req.selector if hasattr(req, "selector") else req.full_url)
        if "approvals" in req.full_url:
            return _response(
                {
                    "id": "s1",
                    "status": "active",
                    "messages": [],
                    "pendingApprovals": [],
                    "usage": {},
                }
            )
        return _response(
            {
                "sessionId": "s1",
                "reply": "done",
                "usage": {},
                "toolCalls": [],
                "events": [],
            }
        )

    with patch("helix_sdk.client.urllib.request.urlopen", side_effect=fake_urlopen):
        client.resolve_approval("s1", "a1", True)
        client.run_schedule("weekend_watch")
    assert any("approvals" in p for p in paths)
    assert any("schedules/run" in p for p in paths)
