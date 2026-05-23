from app.tasks.celery_app import celery_app
from app.tasks.ticket_tasks import process_ticket

__all__ = ["celery_app", "process_ticket"]
