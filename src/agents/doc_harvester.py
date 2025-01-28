"""Documentation harvester pulls relevant docs for the task set by the user of the pipeline."""

import os
from typing import Union
import asyncio
from crawl4ai import AsyncWebCrawler
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# playwright install --with-deps chromium

class DocHarvester:
    """
    Agent for collecting documentation relevant to user's task. Requires internet access.

    More description.

    Attributes
    ----------
    work_dir: str
        Location of the project that Clean Coder pipeline operates on.

    Methods
    -------
        find_documentation(task: str)

    Examples
    --------
        dh = DocHarvester()
        task = "prepare a scraper of a website"
        dh.find_documentation(task=task)
    """

    def __init__(self) -> None:
        """Initial information to help harvest documentation."""
        self.work_dir = os.getenv("WORK_DIR")
    def identify_libraries(self, task: str) -> list[str]:
        """Library names relevant for user's task."""
        libraries = []
        return libraries
    def url_for_library(self, library: str) -> str:
        url = ""
        return url
    def identify_documentation(self, task: str) -> list[str]:
        """Find web addresses of software packages useful for the task."""
        libraries = self.identify_libraries(task=task)
        return [self.url_for_library(library) for library in libraries]
    async def pull_webpage(self, url: str):
        """Pulls URL information."""
        scraped = []
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
            )
            scraped.append(result)
        return scraped
    def find_documentation(self, task: str) -> None | list[str]:
        """Returns documentation relevant for the task set by human user, a list of files."""
        documentation_urls = self.identify_documentation(task=task)
        rag_input = [self.pull_webpage(url=webpage) for webpage in documentation_urls]
        return None
