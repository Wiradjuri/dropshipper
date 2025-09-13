from typing import Any, Dict, List

import stripe
from app.db.session import SessionLocal
from app.orders.models import Order
from app.settings import settings
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

router = APIRouter(prefix="/checkout", tags=["checkout"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/session")
async def create_checkout_session(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.items:
        raise HTTPException(status_code=400, detail="Order has no items")

    success_url = str(request.url_for("health"))  # simple return path
    cancel_url = success_url

    if not settings.STRIPE_SECRET_KEY:
        # Placeholder flow without Stripe keys
        return {"checkout_url": f"/fake-checkout?order_id={order.id}"}

    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items: List[Dict[str, Any]] = [
        {
            "price_data": {
                "currency": order.currency,
                "product_data": {"name": it.name},
                "unit_amount": it.price_cents,
            },
            "quantity": it.quantity,
        }
        for it in order.items
    ]
    session = stripe.checkout.Session.create(  # type: ignore[arg-type]
        mode="payment",
        line_items=line_items,  # type: ignore[arg-type]
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": str(order.id)},
    )
    return {"checkout_url": session.url}
