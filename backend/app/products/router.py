from app.db.session import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import crud, schemas

router = APIRouter(prefix="/products", tags=["products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.ProductOut])
async def list_(db: Session = Depends(get_db)):
    return await crud.list_products(db)

@router.post("/", response_model=schemas.ProductOut)
async def create(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    return await crud.create_product(db, data)

@router.get("/{product_id}", response_model=schemas.ProductOut)
async def get(product_id: int, db: Session = Depends(get_db)):
    p = await crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p

@router.put("/{product_id}", response_model=schemas.ProductOut)
async def update(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    p = await crud.update_product(db, product_id, data)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p

@router.delete("/{product_id}")
async def delete(product_id: int, db: Session = Depends(get_db)):
    ok = await crud.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True}
