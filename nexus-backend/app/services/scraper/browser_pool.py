import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page, Error as PlaywrightError

from app.services.scraper.governance import AcquisitionState

logger = logging.getLogger(__name__)

class BrowserPool:
    """
    Singleton Ingestion Kernel.
    Manages Playwright contexts, memory cleanup, retries, and strict timeout governance.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserPool, cls).__new__(cls)
            cls._instance._playwright: Optional[Playwright] = None
            cls._instance._browser: Optional[Browser] = None
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def initialize(self):
        """Starts the browser runtime if not already active."""
        async with self._lock:
            if not self._browser:
                logger.info("Initializing Browser Runtime...")
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-gpu",
                        "--disable-software-rasterizer"
                    ]
                )
                logger.info("Browser Runtime active.")

    async def _get_context(self) -> BrowserContext:
        """Returns an isolated, reusable context."""
        if not self._browser:
            await self.initialize()
        return await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    async def fetch_page(
        self, 
        url: str, 
        timeout_ms: int = 30000, 
        retries: int = 2
    ) -> Tuple[AcquisitionState, Optional[str], Optional[str], int, str]:
        """
        Fetches the target URL with exponential backoff.
        Enforces memory cleanup and timeout governance.
        
        Returns:
            (AcquisitionState, raw_html, raw_text, fetch_duration_ms, runtime_version)
        """
        start_time = asyncio.get_event_loop().time()
        context = await self._get_context()
        page = await context.new_page()
        
        attempt = 0
        state = AcquisitionState.ACQUISITION_PENDING
        raw_html = None
        raw_text = None
        
        try:
            while attempt <= retries:
                try:
                    logger.info(f"Acquisition Mesh targeting: {url} (Attempt {attempt+1}/{retries+1})")
                    state = AcquisitionState.ACQUISITION_ACTIVE
                    
                    response = await page.goto(
                        url, 
                        timeout=timeout_ms,
                        wait_until="domcontentloaded"
                    )
                    
                    if not response or not response.ok:
                        if response and response.status in [403, 429, 401]:
                            state = AcquisitionState.ACQUISITION_BLOCKED
                            break
                        state = AcquisitionState.ACQUISITION_DEGRADED
                        raise Exception(f"HTTP {response.status if response else 'Unknown'}")
                    
                    # Wait for network idle to ensure React/Vue renders complete
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    
                    raw_html = await page.content()
                    raw_text = await page.evaluate("() => document.body.innerText")
                    state = AcquisitionState.ACQUISITION_COMPLETE
                    break
                    
                except PlaywrightError as pe:
                    logger.warning(f"Playwright Error on {url}: {pe}")
                    attempt += 1
                    if "Timeout" in str(pe):
                        state = AcquisitionState.ACQUISITION_DEGRADED
                    if attempt <= retries:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
                except Exception as e:
                    logger.error(f"Acquisition Error on {url}: {e}")
                    attempt += 1
                    state = AcquisitionState.ACQUISITION_DEGRADED
                    if attempt <= retries:
                        await asyncio.sleep(2 ** attempt)
        
        finally:
            # Deterministic page lifecycle and memory cleanup
            await page.close()
            await context.close()
            
        end_time = asyncio.get_event_loop().time()
        fetch_duration_ms = int((end_time - start_time) * 1000)
        runtime_version = self._browser.version if self._browser else "unknown"
        
        return state, raw_html, raw_text, fetch_duration_ms, runtime_version

    async def close(self):
        """Gracefully terminates the ingestion kernel."""
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None

# Global Kernel Instance
browser_pool = BrowserPool()
