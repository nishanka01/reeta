"""
==================================================
REETA — automation/browser_control.py
==================================================
PURPOSE:
    Provides Playwright-based browser automation.
    Can navigate, search, and extract text from web pages.
==================================================
"""

import threading
import asyncio
from utils.logger import get_logger
from automation.retry_manager import with_automation_retry, AutomationRetryException

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    pass

logger = get_logger(__name__)

class BrowserController:
    """Controls browser actions using Playwright asynchronously."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._loop = asyncio.new_event_loop()
        
        # Start background asyncio loop thread
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._thread.start()
        logger.info("BrowserController initialized.")

    def _start_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run_coro(self, coro):
        """Runs an async coroutine in the background thread."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=30)

    async def _start_browser(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

    async def _navigate(self, url: str):
        await self._start_browser()
        await self.page.goto(url, wait_until="domcontentloaded")
        try:
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except PlaywrightTimeoutError:
            logger.warning(f"Network idle timeout reached for {url}, but DOM is loaded. Proceeding.")

    @with_automation_retry(max_retries=3, base_delay=2.0)
    def open_website(self, url: str) -> str:
        """Opens a website in the automated browser."""
        if not url.startswith("http"):
            url = f"https://{url}"
        
        try:
            self.run_coro(self._navigate(url))
            return f"Opened {url}."
        except Exception as e:
            logger.error(f"Browser navigation failed: {e}")
            return "Failed to open website."

    async def _google_search(self, query: str):
        await self._start_browser()
        await self.page.goto("https://www.google.com", wait_until="domcontentloaded")
        
        # Wait specifically for the search box to be visible
        search_box = self.page.locator("textarea[name='q']")
        await search_box.wait_for(state="visible", timeout=10000)
        
        await search_box.fill(query)
        await search_box.press("Enter")
        
        # Wait for search results container
        await self.page.locator("#search").wait_for(state="visible", timeout=15000)

    @with_automation_retry(max_retries=3, base_delay=2.0)
    def search_google(self, query: str) -> str:
        """Performs a Google search using Playwright."""
        try:
            self.run_coro(self._google_search(query))
            return f"Searched for '{query}'."
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return "Failed to perform search."

    def close(self):
        """Clean up Playwright resources."""
        async def _close():
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        
        try:
            self.run_coro(_close())
        except Exception:
            pass
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
