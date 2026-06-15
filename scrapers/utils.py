import re

PROVINCE_COORDS = {
    "Bangkok":      (13.7563, 100.5018),
    "Chiang Mai":   (18.7883, 98.9853),
    "Chiang Rai":   (19.9105, 99.8406),
    "Phuket":       (7.8804,  98.3923),
    "Chon Buri":    (13.3611, 100.9847),
    "Tak":          (16.8798, 99.1257),
    "Khon Kaen":    (16.4419, 102.8360),
    "Koh Samui":    (9.5120, 100.0136),
    "Nonthaburi":   (13.8621, 100.5144),
    "Samut Prakan": (13.5990, 100.5999),
    "Rayong":       (12.6814, 101.2816),
    "Surat Thani":  (9.1382,  99.3217),
}

DEFAULT_COORDS = (13.7563, 100.5018)  # Bangkok fallback

PROVINCE_ALIASES = {
    "bangkok":     "Bangkok",
    "bkk":         "Bangkok",
    "กรุงเทพ":      "Bangkok",
    "laksi":       "Bangkok",      # DSI HQ district
    "pattaya":     "Chon Buri",
    "พัทยา":        "Chon Buri",
    "ชลบุรี":       "Chon Buri",
    "เชียงใหม่":     "Chiang Mai",
    "เชียงราย":     "Chiang Rai",
    "ภูเก็ต":        "Phuket",
    "นนทบุรี":      "Nonthaburi",
    "สมุทรปราการ":  "Samut Prakan",
    "ขอนแก่น":      "Khon Kaen",
    "ระยอง":        "Rayong",
    "สุราษฎร์ธานี":  "Surat Thani",
    "สมุย":         "Koh Samui",
    "เกาะสมุย":     "Koh Samui",
    "mae sot":     "Tak",
    "myawaddy":    "Tak",
}

CRITICAL_KEYWORDS = [
    "billion", "พันล้าน", "trafficking", "forced labour",
    "rescued", "interpol", "compound", "pig butchering",
]
HIGH_KEYWORDS = [
    "million", "ล้าน", "arrested", "dismantled", "จับกุม", "network", "gang",
]
MEDIUM_KEYWORDS = [
    "warning", "alert", "เตือน", "phishing", "fake", "impersonat",
]

def extract_province(text: str) -> str:
    lower = text.lower()

    for alias, canonical in PROVINCE_ALIASES.items():
        if alias.lower() in lower:
            return canonical

    for province in PROVINCE_COORDS:
        if province.lower() in lower:
            return province

    return "Bangkok"  # most news defaults here if nothing matches


def geocode_province(province: str) -> tuple[float, float]:
    return PROVINCE_COORDS.get(province, DEFAULT_COORDS)

def classify_severity(text: str, default: str = "medium") -> str:
    lower = text.lower()
    if any(k in lower for k in CRITICAL_KEYWORDS):
        return "critical"
    if any(k in lower for k in HIGH_KEYWORDS):
        return "high"
    if any(k in lower for k in MEDIUM_KEYWORDS):
        return "medium"
    return default

def classify_category(text: str, tag_map: dict) -> str:
    lower = text.lower()
    for keyword, category in tag_map.items():
        if keyword.lower() in lower:
            return category
    return "other"

def extract_amount_thb(text: str) -> float:
    """Try to pull a THB amount from text. Handles thousand/million/billion in EN and TH."""
    patterns = [
        (r"฿?\s*(\d[\d,.]+)\s*(?:billion|พันล้าน)", 1_000_000_000),
        (r"฿?\s*(\d[\d,.]+)\s*(?:million|ล้าน)",     1_000_000),
        (r"฿?\s*(\d[\d,.]+)\s*(?:thousand|พัน)",     1_000),
        (r"(\d[\d,.]+)\s*(?:baht|บาท)",              1),
    ]
    for pattern, multiplier in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1).replace(",", ""))
            return amount * multiplier
    return 0.0
