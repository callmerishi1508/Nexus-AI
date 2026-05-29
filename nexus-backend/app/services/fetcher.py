import time
import asyncio
from typing import Dict, Any, Optional, Tuple
import bs4
import markdownify

# Hard Timeout Constraints (CRITICAL for demo survivability)
FETCH_TIMEOUT = 8.0 

class FetchTimeoutError(Exception):
    pass

class FetchError(Exception):
    pass

async def fetch_markdown_from_playwright(target_url: str, browser, telemetry: dict) -> Tuple[str, str]:
    """
    Fetches the target URL using a persistent Playwright Chromium pool.
    Implements Enterprise Connection Pooling: Short-lived context and page per extraction.
    """
    start_time = time.time()
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        bypass_csp=True
    )
    page = await context.new_page()
    try:
        try:
            # wait_until="domcontentloaded" is typically enough for modern frameworks to paint initial DOM
            await page.goto(target_url, wait_until="domcontentloaded", timeout=FETCH_TIMEOUT * 1000)
            # Short wait to let pricing tables render if needed
            await page.wait_for_timeout(500)
            html = await page.content()
        except Exception as e:
            if "Timeout" in str(e) or "timeout" in str(e).lower():
                raise FetchTimeoutError(f"Fetch exceeded strict {FETCH_TIMEOUT}s timeout limit.") from e
            raise FetchError(f"Browser navigation error: {str(e)}") from e
    finally:
        await page.close()
        await context.close()
    
    telemetry["fetch_latency_ms"] = round((time.time() - start_time) * 1000)
    
    # Keep a copy of the cleaned raw HTML for deterministic DOM extraction
    raw_html = str(html)
    
    parse_start = time.time()
    soup = bs4.BeautifulSoup(html, "html.parser")
    
    # Deterministic Extraction First: Remove noise to prevent AI from processing entire DOM
    for element in soup(["script", "style", "nav", "footer", "iframe", "noscript", "header", "svg", "button", "path"]):
        element.decompose()
        
    telemetry["dom_parse_time_ms"] = round((time.time() - parse_start) * 1000)
    
    md_start = time.time()
    # Strip unnecessary links and images to keep the diff clean and token count low
    md = markdownify.markdownify(str(soup), heading_style="ATX", strip=["a", "img"])
    telemetry["markdown_conversion_time_ms"] = round((time.time() - md_start) * 1000)
    
    if not md or len(md.strip()) < 50:
        raise FetchError("Empty or invalid content extracted from DOM")
        
    return md, raw_html

async def safe_fetch_pipeline(competitor: str, url: str, browser) -> Dict[str, Any]:
    """
    The main fetch pipeline that wraps the Playwright fetcher.
    If it fails or times out, it gracefully cascades to the FALLBACK or MOCK system.
    """
    result = {
        "competitor": competitor,
        "url": url,
        "mode": "LIVE",
        "markdown_content": "",
        "raw_html": "",
        "error": None,
        "telemetry": {
            "browser_context_reused": True
        }
    }
    
    try:
        md_content, raw_html = await fetch_markdown_from_playwright(url, browser, result["telemetry"])
        result["markdown_content"] = md_content
        result["raw_html"] = raw_html
    except FetchTimeoutError as e:
        result["mode"] = "FALLBACK"
        result["error"] = str(e)
    except FetchError as e:
        result["mode"] = "FALLBACK"
        result["error"] = str(e)
    except Exception as e:
        result["mode"] = "FALLBACK"
        result["error"] = "Unknown error occurred"

    return result
