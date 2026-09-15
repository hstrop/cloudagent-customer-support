"""Typed API models for CloudAgent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(default="demo-session", min_length=1, max_length=64)


class Evidence(BaseModel):
    id: str
    title: str
    snippet: str
    score: float


class TraceStep(BaseModel):
    name: str
    status: str
    detail: str


class ChatResponse(BaseModel):
    answer: str
    intent: str
    handoff: bool
    session_id: str
    evidence: list[Evidence]
    trace: list[TraceStep]


class ResetResponse(BaseModel):
    reset: bool
    session_id: str
