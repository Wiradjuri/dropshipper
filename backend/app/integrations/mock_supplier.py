import asyncio
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.orders.models import Order

async def place_order_async(order_id: int) -> None:
    # simulate async placement and later tracking availability
    await asyncio.sleep(0)  # yield
    db: Session = SessionLocal()
    try:
        order = db.get(Order, order_id)
        if not order:
            return
        if not order.supplier_order_id:
            order.supplier_order_id = f"MOCK-{order.id}"
            db.add(order)
            db.commit()
    finally:
        db.close()

async def poll_tracking_async(order_id: int) -> None:
    db: Session = SessionLocal()
    try:
        order = db.get(Order, order_id)
        if not order:
            return
        # simulate tracking becoming available after some time
        order.tracking_number = f"TRACK-{order.id}"
        order.status = "fulfilled"
        db.add(order)
        db.commit()
    finally:
        db.close()