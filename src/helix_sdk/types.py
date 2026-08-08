from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    @classmethod
    def from_api(cls, data: dict[str, Any] | None) -> TokenUsage:
        data = data or {}
        return cls(
            prompt_tokens=int(data.get("promptTokens", 0)),
            completion_tokens=int(data.get("completionTokens", 0)),
            total_tokens=int(data.get("totalTokens", 0)),
            estimated_cost_usd=float(data.get("estimatedCostUsd", 0)),
        )


@dataclass
class RunResult:
    session_id: str
    reply: str
    usage: TokenUsage
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    workflow_id: str | None = None
    parked: bool = False
    model_used: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RunResult:
        return cls(
            session_id=str(data["sessionId"]),
            reply=str(data.get("reply", "")),
            usage=TokenUsage.from_api(data.get("usage")),
            tool_calls=list(data.get("toolCalls") or []),
            events=list(data.get("events") or []),
            workflow_id=data.get("workflowId"),
            parked=bool(data.get("parked")),
            model_used=data.get("modelUsed"),
            raw=data,
        )


@dataclass
class SessionRecord:
    id: str
    status: str
    messages: list[dict[str, Any]]
    pending_approvals: list[dict[str, Any]]
    usage: TokenUsage
    workflow_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SessionRecord:
        return cls(
            id=str(data["id"]),
            status=str(data.get("status", "")),
            messages=list(data.get("messages") or []),
            pending_approvals=list(data.get("pendingApprovals") or []),
            usage=TokenUsage.from_api(data.get("usage")),
            workflow_id=data.get("workflowId"),
            raw=data,
        )
