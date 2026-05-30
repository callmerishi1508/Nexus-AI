from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio, sys, logging
from app.api.orchestrator import router as orchestrator_router
from app.api.events import router as events_router
from app.governance.review_queue import router as governance_router
from app.chaos.injector import router as chaos_router
from app.api.snapshots import router as snapshots_router
from app.api.simulation import router as simulation_router
from app.api.system import router as system_router
from app.api.targets import router as targets_router
from app.api.copilot import router as copilot_router
from app.api.ingestion import router as ingestion_router

logger = logging.getLogger("nexus.infrastructure")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup tasks...
    yield
    # shutdown tasks...

# ✅ Ye block lifespan ke baad hona chahiye, indent nahi hona chahiye
app = FastAPI(
    title="NEXUS Backend",
    description="Governed Event-Driven Intelligence Infrastructure",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(orchestrator_router, prefix="/api/demo")
app.include_router(events_router, prefix="/api/demo")
app.include_router(governance_router, prefix="/api/governance")
# ... baaki routers

@app.get("/health")
async def health_check():
    return {"status": "operational", "system": "NEXUS"}
