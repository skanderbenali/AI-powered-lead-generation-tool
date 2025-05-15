from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def create_celery():
    """Create and configure Celery app"""
    celery = Celery(
        "scraper",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["app.tasks"]
    )
    
    # Configure Celery
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
        broker_connection_retry_on_startup=True
    )
    
    return celery


celery_app = create_celery()


if __name__ == "__main__":
    celery_app.start()
