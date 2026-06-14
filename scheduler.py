import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scrapers import run_all_scrapers
from models import save_incidents

logger = logging.getLogger(__name__)
_scheduler = None

def scrape_job():
    logger.info("[scheduler] Starting scrape run at %s", datetime.now().isoformat())

    incidents = run_all_scrapers()
    new_count = save_incidents(incidents)

    logger.info("[scheduler] Done. %d scraped, %d new saved.", len(incidents), new_count)

def start_scheduler(interval_hours: int = 6):
    global _scheduler

    if _scheduler and _scheduler.running:
        return  # already running, don't start a second one

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        scrape_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id="scrape_job",
        replace_existing=True,
        next_run_time=datetime.now(),  # run once immediately on startup
    )
    _scheduler.start()
    logger.info("[scheduler] Started. Interval = %dh", interval_hours)


def stop_scheduler():
    if _scheduler:
        _scheduler.shutdown()
