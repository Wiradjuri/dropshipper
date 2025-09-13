from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Product
from .schemas import ProductCreate, ProductUpdate


async def list_products(db: Session):
    return db.execute(select(Product)).scalars().all()

async def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)

async def create_product(db: Session, data: ProductCreate):
    p = Product(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

async def update_product(db: Session, product_id: int, data: ProductUpdate):
    p = db.get(Product, product_id)
    if not p:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

async def delete_product(db: Session, product_id: int):
    p = db.get(Product, product_id)
    if not p:
        return False
    db.delete(p)
    db.commit()
    return True
