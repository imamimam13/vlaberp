from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import Product
from backend.app.schemas.schemas import ProductOut

router = APIRouter(prefix="/inventory", tags=["inventory"])

class CreateProductRequest(BaseModel):
    company_id: int
    sku: str
    name: str
    product_type: str = "raw_material"
    uom: str = "pcs"
    cost_price: float = 0.0
    list_price: float = 0.0
    current_stock: float = 0.0
    min_safety_stock: float = 20.0

class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    cost_price: Optional[float] = None
    list_price: Optional[float] = None
    current_stock: Optional[float] = None
    min_safety_stock: Optional[float] = None

@router.get("/products/{company_id}", response_model=List[ProductOut])
def list_products(company_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.company_id == company_id).all()

@router.post("/products", response_model=ProductOut)
def create_product(payload: CreateProductRequest, db: Session = Depends(get_db)):
    p = Product(
        company_id=payload.company_id,
        sku=payload.sku,
        name=payload.name,
        product_type=payload.product_type,
        uom=payload.uom,
        cost_price=payload.cost_price,
        list_price=payload.list_price,
        current_stock=payload.current_stock,
        min_safety_stock=payload.min_safety_stock
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: UpdateProductRequest, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    if payload.name is not None: p.name = payload.name
    if payload.cost_price is not None: p.cost_price = payload.cost_price
    if payload.list_price is not None: p.list_price = payload.list_price
    if payload.current_stock is not None: p.current_stock = payload.current_stock
    if payload.min_safety_stock is not None: p.min_safety_stock = payload.min_safety_stock
    db.commit()
    db.refresh(p)
    return p

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    db.delete(p)
    db.commit()
    return {"status": "success", "message": f"Produk '{p.name}' berhasil dihapus"}
