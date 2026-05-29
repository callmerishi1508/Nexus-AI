from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router as graph_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Nexus Intelligence Graph API",
    description="Stateless querying layer for the Materialized Signal Graph",
    version="1.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router, prefix="/api/intelligence", tags=["Intelligence Projections"])

@app.get("/health")
def health_check():
    return {"status": "ok", "subsystems": ["acquisition", "graph_orchestrator"]}
