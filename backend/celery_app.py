from celery import Celery

celery = Celery(
    "placement_portal",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.timezone = "Asia/Kolkata"

celery.conf.beat_schedule = {
    "monthly-placement-report": {
        "task": "tasks.monthly_report",
        "schedule": {
            "type": "crontab",
            "minute": 0,
            "hour": 9,
            "day_of_month": 1
        }
    }
}