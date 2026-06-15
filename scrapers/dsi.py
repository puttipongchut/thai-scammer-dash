import re
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup

from scrapers import BaseScraper, ScrapedIncident
from scrapers.utils import extract_province, geocode_province, classify_severity, classify_category, extract_amount_thb

logger = logging.getLogger(__name__)

BASE_URL = "https://www.dsi.go.th"
LIST_URL = f"{BASE_URL}/en/Type/Mission-News/1"

DATE_PATTERN = re.compile(r"\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s*[AP]M")

TAG_MAP = {
    "หลอกให้ลงทุน": "investment",
    "ลงทุน":        "investment",
    "forex":        "investment",
    "คริปโต":       "investment",
    "crypto":       "investment",
    "ดอกเบี้ย":      "investment",
    "คอลเซ็นเตอร์":  "callcenter",
    "บัญชีม้า":      "callcenter",
    "call center":  "callcenter",
    "นอมินี":        "realestate",
    "หลอกลวง":      "phishing",
    "ฉ้อโกง":        "phishing",
    "romance":      "romance",
    "โรแมนซ์":       "romance",
}


class DSIScraper(BaseScraper):
    name = "dsi"

    def scrape(self) -> list[ScrapedIncident]:
        resp = self.session.get(LIST_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        incidents = []
        seen_urls = set()

        for link in soup.select('a[href*="/en/Detail/"]'):
            title = link.get("title", "").strip()
            href  = link.get("href", "")

            if not title or href in seen_urls:
                continue
            seen_urls.add(href)

            category = classify_category(title, TAG_MAP)
            if category == "other":
                continue

            url = href if href.startswith("http") else BASE_URL + href
            published_at = _find_nearby_date(link)

            # Fetch the article body
            time.sleep(1)
            body_text, summary = self._fetch_article_detail(url)

            combined  = title + " " + body_text
            province  = extract_province(combined)
            severity  = classify_severity(combined, default="high")
            amount    = extract_amount_thb(combined)
            lat, lng  = geocode_province(province)

            incidents.append(ScrapedIncident(
                title=title,
                summary=summary or "DSI case update — see source for full details.",
                source="DSI Thailand",
                source_url=url,
                published_at=published_at,
                province=province,
                category=category,
                severity=severity,
                lat=lat,
                lng=lng,
                amount_thb=amount,
            ))

        return incidents

    def _fetch_article_detail(self, url: str) -> tuple[str, str]:
        """Returns (full_body_text, short_summary). Falls back to ("", "") on any failure."""
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            h1 = soup.find("h1")
            if not h1:
                return "", ""

            paragraphs = []
            for el in h1.find_all_next():
                if el.name in ("h2", "h3"):
                    break 
                if el.name == "p":
                    text = el.get_text(strip=True)
                    if text:
                        paragraphs.append(text)

            full_text = " ".join(paragraphs)

            summary = max(paragraphs, key=len, default="")
            if len(summary) > 280:
                summary = summary[:277].rsplit(" ", 1)[0] + "…"

            return full_text, summary
        except Exception as e:
            logger.warning("[dsi] failed to fetch detail %s: %s", url, e)
            return "", ""


def _find_nearby_date(tag) -> datetime:
    node = tag
    for _ in range(4):
        node = node.parent
        if node is None:
            break
        match = DATE_PATTERN.search(node.get_text())
        if match:
            try:
                return datetime.strptime(match.group(), "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                pass
    return datetime.now()


if __name__ == "__main__":
    import json
    scraper = DSIScraper()
    results = scraper.safe_scrape()
    print(f"Found {len(results)} scam-related incidents\n")
    for r in results[:5]:
        print(json.dumps(r.__dict__, default=str, indent=2, ensure_ascii=False))
        