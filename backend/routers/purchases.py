from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import database
import schemas
import crud

router = APIRouter(
    prefix="/purchases",
    tags=["purchases"],
)

@router.post("/", response_model=schemas.PurchaseBatch)
async def create_purchase_batch(batch: schemas.PurchaseBatchCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_purchase_batch(db=db, batch=batch)

@router.get("/", response_model=List[schemas.PurchaseBatch])
async def read_purchase_batches(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_purchase_batches(db, skip=skip, limit=limit)
