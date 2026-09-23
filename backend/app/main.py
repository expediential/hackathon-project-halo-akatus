from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.routes import alerts, dashboard, incidents, reports
from app.core.config import get_settings
from app.db.database import SessionLocal, init_db
from app.services.websocket_manager import manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="ATOM HALO Emergency API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(reports.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "atom-halo-emergency-api"}


@app.websocket("/ws/incidents")
async def incidents_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
