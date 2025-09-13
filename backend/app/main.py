from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.products.router import router as products_router
from app.orders.router import router as orders_router
from app.checkout.router import router as checkout_router
from app.webhooks.router import router as webhooks_router
from apscheduler.schedulers.background import BackgroundScheduler
from app.integrations.mock_supplier import poll_tracking_async
from app.config import settings

def schedule_tracking_poll(order_id: int):
    # schedule a poll in 10 seconds
    scheduler.add_job(lambda: __import__('asyncio').run(poll_tracking_async(order_id)), trigger='date')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(checkout_router)
app.include_router(webhooks_router)

scheduler = BackgroundScheduler()
scheduler.start()
