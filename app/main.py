from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import transactions, health 

app = FastAPI(title="Transaction Webhook Service")

origins = [
    "http://localhost:3000", 
    "http://localhost:5173", 
    "https://walnutpay.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(transactions.router, prefix="/v1")
