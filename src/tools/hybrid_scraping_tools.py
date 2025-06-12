import asyncio
import logging
from typing import Optional, Dict, Any
from crewai_tools import BaseTool, FirecrawlScrapeWebsiteTool, FirecrawlSearchTool
from crawl4ai import AsyncWebCrawler
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class HybridScrapeTool(BaseTool):
    name: str = "hybrid_scrape_website"
    description: str = "Scrape website content using Crawl4AI with Firecrawl fallback"
    
    def _run(self, url: str, **kwargs) -> str:
        """Scrape website with Crawl4AI primary, Firecrawl fallback."""
        try:
            result = asyncio.run(self._crawl4ai_scrape(url))
            if result:
                logger.info(f"Successfully scraped {url} with Crawl4AI")
                return result
        except Exception as e:
            logger.warning(f"Crawl4AI failed for {url}: {e}")
        
        try:
            logger.info(f"Falling back to Firecrawl for {url}")
            firecrawl_tool = FirecrawlScrapeWebsiteTool()
            return firecrawl_tool._run(url, **kwargs)
        except Exception as e:
            logger.error(f"Both Crawl4AI and Firecrawl failed for {url}: {e}")
            return f"Error scraping {url}: {e}"
    
    async def _crawl4ai_scrape(self, url: str) -> Optional[str]:
        """Scrape using Crawl4AI AsyncWebCrawler."""
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url)
            if result and result.markdown:
                return result.markdown
            return None

class HybridSearchTool(BaseTool):
    name: str = "hybrid_search"
    description: str = "Search the web using Crawl4AI with Firecrawl fallback"
    
    def _run(self, query: str, **kwargs) -> str:
        """Search with Crawl4AI primary, Firecrawl fallback."""
        try:
            firecrawl_tool = FirecrawlSearchTool()
            return firecrawl_tool._run(query, **kwargs)
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return f"Error searching for '{query}': {e}"
