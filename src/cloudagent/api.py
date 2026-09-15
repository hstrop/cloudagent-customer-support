"""FastAPI entry point for the CloudAgent demo."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import ChatRequest, ChatResponse, ResetResponse
from .service import KNOWLEDGE, CloudAgent


def create_app() -> FastAPI:
    application = FastAPI(
        title="CloudAgent Customer Support API",
        version="0.1.0",
        description="Offline-first customer support workflow with evidence and human handoff",
    )
    application.state.agent = CloudAgent()
    static_dir = Path(__file__).parent / "static"
    application.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @application.get("/", include_in_schema=False)
    async def frontend() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @application.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "mode": "offline_demo", "knowledge_items": len(KNOWLEDGE)}

    @application.get("/v1/knowledge")
    async def knowledge() -> list[dict[str, str]]:
        return [{"id": item.id, "title": item.title} for item in KNOWLEDGE]

    @application.post("/v1/chat", response_model=ChatResponse)
    async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
        try:
            return request.app.state.agent.chat(payload.message, payload.session_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/v1/sessions/{session_id}/reset", response_model=ResetResponse)
    async def reset(session_id: str, request: Request) -> ResetResponse:
        try:
            reset_done = request.app.state.agent.reset(session_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return ResetResponse(reset=reset_done, session_id=session_id)

    return application


app = create_app()
