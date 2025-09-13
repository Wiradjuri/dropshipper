from pydantic import BaseModel, Field
from typing import List

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

class OrderCreate(BaseModel):
    items: List[OrderItemIn]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    name: str
    sku: str
    price_cents: int
    quantity: int

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    status: str
    currency: str
    subtotal_cents: int
    total_cents: int
    items: List[OrderItemOut]
    supplier_order_id: str | None = None
    tracking_number: str | None = None

    class Config:
        from_attributes = True
