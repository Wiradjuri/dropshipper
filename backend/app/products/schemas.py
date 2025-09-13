from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    sku: str = Field(min_length=1)
    price_cents: int = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    description: Optional[str] = None
    image_url: Optional[str] = None
    stock: int = Field(ge=0, default=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price_cents: Optional[int] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    description: Optional[str] = None
    image_url: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)

class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True
