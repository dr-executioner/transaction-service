from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.transaction import Transaction
from app.core.database import AsyncSession, get_session
from app.core.celery_app import celery_app
import asyncio
import redis.asyncio as redis_client
from app.core.config import settings
from app.utils.helper import run_async

redis = None

async def init_redis():
    global redis
    if redis is None:
        redis = redis_client.from_url(settings.REDIS_URL)

@celery_app.task(bind=True, name="app.services.transaction_service.process_transaction_task")
def process_transaction_task(self, transaction_data):
    run_async(process_transaction(transaction_data))

async def process_transaction(transaction_data: dict):
    await init_redis()

    transaction_id = transaction_data["transaction_id"]
    # Idempotency check
    if await redis.get(transaction_id):
        return

    # Mark as processing with expiration
    await redis.set(transaction_id, "processing", ex=3600)

    async with get_session() as session:
        # Check if transaction exists in DB
        stmt = select(Transaction).filter(Transaction.transaction_id == transaction_id)
        result = await session.execute(stmt)
        existing = result.scalars().first()
        if existing:
            await redis.delete(transaction_id)
            return

        # Simulate external call delay
        # await asyncio.sleep(30)

        # Insert transaction with status PROCESSED
        new_txn = Transaction(
            transaction_id=transaction_id,
            source_account=transaction_data["source_account"],
            destination_account=transaction_data["destination_account"],
            amount=transaction_data["amount"],
            currency=transaction_data["currency"],
            status="PROCESSED",
            processed_at=datetime.utcnow()
        )
        session.add(new_txn)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        finally:
            await redis.delete(transaction_id)
