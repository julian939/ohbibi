from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import utils.file_loader as file_loader
import logging

logger = logging.getLogger(__name__)

class AbstractScraper:

    def __init__(self):
        self.base_url = "https://portal.abs.xyz/stream/"
        self.stream_config = file_loader.load_stream_config()

    async def _fetch_html(self, url: str):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=15000)

                try:
                    await page.wait_for_selector("h2.h3", timeout=8000)
                except:
                    pass  

                content = await page.content()
                await browser.close()
                return content
        except Exception:
            logger.exception(f"Failed to fetch Abstract stream HTML for {url}")
            return ""

    async def is_live(self, username: str) -> bool:
        html = await self._fetch_html(f"{self.base_url}{username}")
        return "live" in html.lower()

    async def get_title(self, username: str):
        html = await self._fetch_html(f"{self.base_url}{username}")
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("h2", class_="h3")
        return title.text.strip() if title else None

    async def check_stream_title_for_keywords(self, username: str):
        title = await self.get_title(username)
        keywords = self.stream_config.get("stream_categories", [])
        return any(k.lower() in title.lower() for k in keywords) if title else False