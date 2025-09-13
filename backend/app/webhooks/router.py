import asyncio

import stripe
from app.db.session import SessionLocal
from app.emails.service import send_receipt
from app.integrations.mock_supplier import place_order_async, poll_tracking_async
from app.orders.models import Order
from app.settings import settings
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        # In dev without secrets, accept payload directly
        payload = await request.json()
        event_type = payload.get("type")
        data = payload.get("data", {}).get("object", {})
    else:
        sig_header = request.headers.get("Stripe-Signature")
        body = await request.body()
        try:
            # stripe.Webhook.construct_event(payload, sig_header, secret)
            event = stripe.Webhook.construct_event(body, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid signature")
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed" or event_type == "payment_intent.succeeded":
        order_id = int((data.get("metadata") or {}).get("order_id", 0))
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "paid":
            order.status = "paid"  # type: ignore[assignment]
            db.add(order)
            db.commit()
            # Trigger supplier placement
            await place_order_async(int(order.id))
            # Send receipt (stub)
            send_receipt(int(order.id))
            # Schedule tracking update in ~5 seconds
            async def _delayed_tracking():
                await asyncio.sleep(5)
                await poll_tracking_async(int(order.id))
            asyncio.create_task(_delayed_tracking())
        return {"received": True}

    return {"ignored": True}