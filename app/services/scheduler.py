from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.feed_service import FeedService
from app.core.config import settings

scheduler = BackgroundScheduler()
feed_service = FeedService()

def process_feeds_job():
    """Job to process all RSS feeds."""
    feed_service.process_all_feeds()

# Add the job to the scheduler
scheduler.add_job(
    process_feeds_job,
    trigger=IntervalTrigger(minutes=settings.SCHEDULE_INTERVAL_MINUTES),
    id='process_feeds',
    name='Process RSS feeds',
    replace_existing=True
) 