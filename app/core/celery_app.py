from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.task_routes = {"app.services.transaction_service.process_transaction_task": {"queue": "transactions"}}


import app.services.transaction_service