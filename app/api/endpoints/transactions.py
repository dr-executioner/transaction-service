from fastapi import APIRouter, Depends, HTTPException
from app.services.transaction_service import process_transaction_task
from pydantic import BaseModel, Field
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.transaction import Transaction

router = APIRouter()

class TransactionWebhook(BaseModel):
    transaction_id: str = Field(..., example="txn_abc123def456")
    source_account: str = Field(..., example="acc_user_789")
    destination_account: str = Field(..., example="acc_merchant_456")
    amount: float = Field(..., example=1500)
    currency: str = Field(..., example="INR")

@router.post("/webhooks/transactions", status_code=202)
async def receive_webhook(payload: TransactionWebhook):
    print("Transaction Payload inside receive_webhook", payload)
    process_transaction_task.delay(payload.dict())
    return {"message": "Accepted for processing"}

@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str, session: AsyncSession = Depends(get_session)):
    print("Transaction Id in Post Route",transaction_id )
    stmt = select(Transaction).filter(Transaction.transaction_id == transaction_id)
    result = await session.execute(stmt)
    transaction = result.scalars().first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "transaction_id": transaction.transaction_id,
        "source_account": transaction.source_account,
        "destination_account": transaction.destination_account,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "status": transaction.status,
        "created_at": transaction.created_at.isoformat()+"Z",
        "processed_at": transaction.processed_at.isoformat()+"Z" if transaction.processed_at else None,
    }
