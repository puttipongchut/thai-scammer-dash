import re
from datetime import datetime
from bs4 import BeautifulSoup

from scrapers import BaseScraper, ScrapedIncident
from scrapers.utils import extract_province, geocode_province, classify_severity, classify_category, extract_amount_thb

BASE_URL = "https://www.dsi.go.th"
LIST_URL = f"{BASE_URL}/en/Type/Mission-News/2"

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
                continue  # skip non-scam news

            url = href if href.startswith("http") else BASE_URL + href

            published_at = _find_nearby_date(link)

            province = extract_province(title)
            severity = classify_severity(title, default="high")
            amount   = extract_amount_thb(title)
            lat, lng = geocode_province(province)

            incidents.append(ScrapedIncident(
                title=title,
                summary="DSI case update — see source for full details.",
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

def _find_nearby_date(tag) -> datetime:
    """Walk up a few ancestor levels looking for a M/D/YYYY H:MM:SS AM/PM string."""
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
