from celery import Celery

celery=Celery(
    'tasks',
    broker='redis://127.0.0.1:6379/0'
)

celery.conf.timezone = 'Asia/Kolkata'
celery.conf.enable_utc = False

from app import app

@celery.task()
