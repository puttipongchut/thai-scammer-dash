PROVINCE_COORDS = {
    "Bangkok":      (13.7563, 100.5018),
    "Chiang Mai":   (18.7883, 98.9853),
    "Phuket":       (7.8804,  98.3923),
    "Chon Buri":    (13.3611, 100.9847),
    "Tak":          (16.8798, 99.1257),
    "Khon Kaen":    (16.4419, 102.8360),
    "Koh Samui":    (9.5120, 100.0136),
}

DEFAULT_COORDS = (13.7563, 100.5018)  # Bangkok fallback

PROVINCE_ALIASES = {
    "bangkok":     "Bangkok",
    "bkk":         "Bangkok",
    "กรุงเทพ":      "Bangkok",
    "pattaya":     "Chon Buri",
    "พัทยา":        "Chon Buri",
    "เชียงใหม่":     "Chiang Mai",
    "ภูเก็ต":        "Phuket",
    "mae sot":     "Tak",        # border town in Tak province
    "myawaddy":    "Tak",        # Myanmar border, often appears in scam-compound news
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

province = extract_province(title + " " + summary)
lat, lng = geocode_province(province)

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