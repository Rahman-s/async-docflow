from celery import Celery
from app.core.config import settings

celery = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery.conf.task_routes = {
    "app.workers.tasks.process_document_task": {"queue": "documents"}
}