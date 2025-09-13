from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import SessionLocal
from app.products.models import Product
from .models import Order, OrderItem
from .schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

TAX_RATE = 0.0  # MVP: no tax

@router.post("/", response_model=OrderOut)
async def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items")

    # Fetch products and compute totals from server-side authoritative data
    subtotal = 0
    currency = None
    order = Order(status="pending")
    db.add(order)
    db.flush()  # get order.id

    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Invalid product {item.product_id}")
        if currency is None:
            currency = product.currency
        elif currency != product.currency:
            raise HTTPException(status_code=400, detail="Mixed currency not supported")
        line_subtotal = product.price_cents * item.quantity
        subtotal += line_subtotal
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            name=product.name,
            sku=product.sku,
            price_cents=product.price_cents,
            quantity=item.quantity,
        ))

    total = int(subtotal * (1 + TAX_RATE))
    order.subtotal_cents = subtotal
    order.total_cents = total
    order.currency = currency or "USD"
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
