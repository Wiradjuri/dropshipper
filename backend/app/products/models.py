from sqlalchemy import Column, Integer, String, Text
from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(64), nullable=False, index=True)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    description = Column(Text, nullable=True)
    image_url = Column(String(1024), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
