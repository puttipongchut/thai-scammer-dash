import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
from datetime import datetime
from models import init_db, get_recent_incidents
from scheduler import start_scheduler

app = Flask(__name__)

# DB
init_db()

# Scheduler
interval = int(os.environ.get("SCRAPE_INTERVAL_HOURS", 6))
if interval > 0:
    start_scheduler(interval_hours=interval) 

CATEGORIES = {
    "investment": {"label": "Investment / Crypto",      "color": "#A6362C"},
    "romance":    {"label": "Romance Scam",              "color": "#C1672E"},
    "phishing":   {"label": "Phishing / Impersonation",  "color": "#B6862C"},
    "ecommerce":  {"label": "E-Commerce Fraud",          "color": "#1F3A52"},
    "callcenter": {"label": "Call Centre",               "color": "#6E5B7B"},
    "malware":    {"label": "Malware / App",             "color": "#4B7755"},
    "realestate": {"label": "Real Estate",               "color": "#5C6470"},
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/incidents")
def api_incidents():
    incidents = get_recent_incidents(limit=500)
    features = []
    for inc in incidents:
        if not inc.lat or not inc.lng:
            continue
        cat_meta = CATEGORIES.get(inc.category, {})
        props = inc.to_dict()
        props["categoryLabel"] = cat_meta.get("label", inc.category)
        props["categoryColor"] = cat_meta.get("color", "#5C6470")
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [inc.lng, inc.lat]},
            "properties": props,
        })
    return jsonify({"type": "FeatureCollection", "features": features})

@app.route("/api/stats")
def api_stats():
    incidents = get_recent_incidents(limit=500)

    total_victims  = sum(i.victims or 0 for i in incidents)
    total_amount   = sum(i.amount_thb or 0 for i in incidents)
    critical_count = sum(1 for i in incidents if i.severity == "critical")
    provinces      = len({i.province for i in incidents if i.province})

    by_category = {}
    for inc in incidents:
        cat = inc.category or "other"
        if cat not in by_category:
            by_category[cat] = {
                "count": 0, "victims": 0, "amount": 0,
                "label": CATEGORIES.get(cat, {}).get("label", cat),
                "color": CATEGORIES.get(cat, {}).get("color", "#5C6470"),
            }
        by_category[cat]["count"]   += 1
        by_category[cat]["victims"] += inc.victims or 0
        by_category[cat]["amount"]  += inc.amount_thb or 0

    return jsonify({
        "totalIncidents":  len(incidents),
        "totalVictims":    total_victims,
        "totalAmountTHB":  total_amount,
        "criticalAlerts":  critical_count,
        "activeProvinces": provinces,
        "byCategory":      by_category,
        "lastUpdated":     datetime.now().isoformat(),
    })


@app.route("/api/recent")
def api_recent():
    incidents = get_recent_incidents(limit=10)
    return jsonify([i.to_dict() for i in incidents])

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
    