from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .types import RunResult, SessionRecord


class HelixError(Exception):
    def __init__(self, message: str, status: int, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


class HelixClient:
    """Typed client for a running Helix console (`helix console`)."""

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def agent(self) -> dict[str, Any]:
        return self._request("GET", "/helix/v1/agent")

    def stack(self) -> dict[str, Any]:
        return self._request("GET", "/helix/v1/stack")

    def sessions(self) -> list[SessionRecord]:
        data = self._request("GET", "/helix/v1/sessions")
        return [SessionRecord.from_api(item) for item in data]

    def workflows(self, session_id: str | None = None) -> list[dict[str, Any]]:
        qs = f"?sessionId={urllib.parse.quote(session_id)}" if session_id else ""
        return self._request("GET", f"/helix/v1/workflows{qs}")

    def events(self, session_id: str | None = None) -> list[dict[str, Any]]:
        qs = f"?sessionId={urllib.parse.quote(session_id)}" if session_id else ""
        return self._request("GET", f"/helix/v1/events{qs}")

    def run(
        self,
        message: str,
        *,
        session_id: str | None = None,
        auto_approve: bool = False,
        channel: str = "http",
    ) -> RunResult:
        data = self._request(
            "POST",
            "/helix/v1/sessions",
            {
                "message": message,
                "sessionId": session_id,
                "autoApprove": auto_approve,
                "channel": channel,
            },
        )
        return RunResult.from_api(data)

    def chat(
        self,
        message: str,
        session_id: str | None = None,
        *,
        auto_approve: bool = False,
        channel: str = "http",
    ) -> RunResult:
        return self.run(
            message,
            session_id=session_id,
            auto_approve=auto_approve,
            channel=channel,
        )

    def resolve_approval(
        self,
        session_id: str,
        approval_id: str,
        approve: bool,
    ) -> SessionRecord:
        data = self._request(
            "POST",
            "/helix/v1/approvals",
            {
                "sessionId": session_id,
                "approvalId": approval_id,
                "approve": approve,
            },
        )
        return SessionRecord.from_api(data)

    def run_schedule(self, name: str) -> RunResult:
        data = self._request("POST", "/helix/v1/schedules/run", {"name": name})
        return RunResult.from_api(data)

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                raw = res.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8")
            try:
                parsed: Any = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            message = (
                parsed.get("error")
                if isinstance(parsed, dict) and isinstance(parsed.get("error"), str)
                else f"Helix HTTP {err.code}"
            )
            raise HelixError(message, err.code, parsed) from err
