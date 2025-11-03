from fastapi import FastAPI
from app.api.endpoints import transactions, health

app = FastAPI(title="Transaction Webhook Service")

app.include_router(health.router)
app.include_router(transactions.router, prefix="/v1")

