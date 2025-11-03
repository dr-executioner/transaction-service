from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True)
    source_account = Column(String, nullable=False)
    destination_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PROCESSING")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
