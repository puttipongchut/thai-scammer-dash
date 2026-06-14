from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import abc
import logging
import httpx


@dataclass
class ScrapedIncident:
    title:        str
    summary:      str
    source:       str
    source_url:   str
    published_at: datetime
    province:     str
    category:     str      # investment | romance | phishing | ecommerce | callcenter | malware | realestate
    severity:     str      # critical | high | medium | low
    lat:          float
    lng:          float
    victims:      int            = 0
    amount_thb:   float          = 0.0
    tags:         list[str]      = field(default_factory=list)
    raw_html:     Optional[str]  = field(default=None, repr=False)

logger = logging.getLogger(__name__)


class BaseScraper(abc.ABC):

    name: str = "base"

    def __init__(self):
        self.session = httpx.Client(
            headers={"User-Agent": "ScamRadarBot/1.0 (civic research; contact@yourdomain.com)"},
            timeout=30,
            follow_redirects=True,
        )

    @abc.abstractmethod
    def scrape(self) -> list[ScrapedIncident]:
        ...

    def safe_scrape(self) -> list[ScrapedIncident]:
        try:
            results = self.scrape()
            logger.info("[%s] returned %d incidents", self.name, len(results))
            return results
        except Exception as e:
            logger.error("[%s] failed: %s", self.name, e, exc_info=True)
            return []
    
def run_all_scrapers() -> list[ScrapedIncident]:
    # from scrapers.police import RTPNewsScraper

    scrapers = [
        # RTPNewsScraper(),
    ]

    results = []
    for s in scrapers:
        results.extend(s.safe_scrape())
    return results
