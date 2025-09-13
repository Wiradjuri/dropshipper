import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.orders.models import Order

log = logging.getLogger(__name__)

def send_receipt(order_id: int) -> None:
  db: Session = SessionLocal()
  try:
    order = db.get(Order, order_id)
    if not order:
      return
    # Stub: log the receipt instead of sending via provider
    log.info("[EMAIL] Receipt for order %s total=%s %s", order.id, order.total_cents/100, order.currency)
  finally:
    db.close()
