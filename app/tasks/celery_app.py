from celery import Celery

from app.config import settings

celery_app = Celery(
    "supports_triager",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.autodiscover_tasks(["app.tasks"])
