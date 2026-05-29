from contextlib import asynccontextmanager
# Reload trigger to clear potential DB locks
from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
from app.services.watcher import watcher_service
from app.services.inference_router import inference_router
from app.services.daemons import governance_daemon
from app.db.models import Base, engine
from app.db.seed import seed_data
from app.config.settings import settings
import logging

logger = logging.getLogger("nexus.infrastructure")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("CURRENT EVENT LOOP:", type(asyncio.get_running_loop()))
    # Ensure SQLite tables exist
    print("Initializing SQLite schemas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Seeding isolated tenant environments...")
    await seed_data()

    # Stage 2: Proprietary Ingestion - Initialize persistent Playwright Chromium pool
    logger.info("Initializing Enterprise Ingestion Pool...")
    playwright = await async_playwright().start()
    
    browser = None
    if settings.BRIGHT_DATA_SCRAPING_BROWSER_URL:
        try:
            logger.info("Attempting connection to Bright Data Scraping Browser...")
            browser = await playwright.chromium.connect_over_cdp(settings.BRIGHT_DATA_SCRAPING_BROWSER_URL, timeout=10000)
            version = browser.version
            logger.info(f"Successfully connected to Bright Data Scraping Browser (Version: {version})")
        except Exception as e:
            logger.warning(f"Bright Data Scraping Browser unavailable: {str(e)}. Falling back to local Chromium...")
            browser = None
            
    if not browser:
        logger.info("Launching local Chromium mesh (Fallback Mode)...")
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        version = browser.version
        logger.info(f"Local Chromium initialized (Version: {version})")
    
    # Connection Pooling Architecture:
    # Browser: Shared globally
    # Context: Created per task/job to prevent memory leaks
    # Page: Short-lived per extraction
    
    app.state.playwright = playwright
    app.state.browser = browser
    logger.info("Ingestion Pool Ready.")
    
    # Stage 5: Cold Start Protection for Sovereign Inference
    await inference_router.warm_up()
    
    # Phase 18: Autonomous Governance Agents
    print("Starting Autonomous Governance Daemon...")
    governance_daemon.start()
    
    # Stage 4: Event-Driven Intelligence Activation
    print("Starting Continuous Intelligence Watcher...")
    await watcher_service.start(app.state)
    print("Watcher Active.")
    
    yield
    
    # Graceful shutdown
    logger.info("Shutting down Continuous Intelligence Watcher...")
    watcher_service.shutdown()
    logger.info("Shutting down Autonomous Governance Daemon...")
    governance_daemon.stop()
    logger.info("Shutting down Ingestion Pool...")
    if hasattr(app.state, "browser") and app.state.browser:
        await app.state.browser.close()
    if hasattr(app.state, "playwright") and app.state.playwright:
        await app.state.playwright.stop()

app = FastAPI(
    title="NEXUS Backend",
    description="Governed Event-Driven Intelligence Infrastructure",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orchestrator_router, prefix="/api/demo")
app.include_router(events_router, prefix="/api/demo")
app.include_router(governance_router, prefix="/api/governance")
app.include_router(targets_router, prefix="/api/governance/targets")
app.include_router(chaos_router, prefix="/api/chaos")
app.include_router(snapshots_router, prefix="/api/system/snapshot")
app.include_router(copilot_router, prefix="/api/copilot")
app.include_router(ingestion_router, prefix="/api/ingestion")
app.include_router(system_router)
app.include_router(simulation_router)
from app.api.routes import router as intelligence_router
app.include_router(intelligence_router, prefix="/api/intelligence")

@app.get("/health")
async def health_check():
    return {"status": "operational", "system": "NEXUS"}
