from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import database
import schemas
import crud

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.post("/", response_model=schemas.Product)
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_product(db=db, product=product)

@router.get("/", response_model=List[schemas.Product])
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_products(db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=schemas.Product)
async def read_product(product_id: str, db: AsyncSession = Depends(database.get_db)):
    db_product = await crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
