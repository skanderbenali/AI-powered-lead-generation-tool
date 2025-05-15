import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "lead_generation",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.services.tasks.email_tasks",
        "app.services.tasks.scraper_tasks",
        "app.services.tasks.lead_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=200,
)

if __name__ == "__main__":
    celery_app.start()
