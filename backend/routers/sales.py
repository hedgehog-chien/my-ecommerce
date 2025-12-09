from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import database
import schemas
import crud
import import_service

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
)

@router.post("/", response_model=schemas.Order)
async def create_sales_order(order: schemas.OrderCreate, db: AsyncSession = Depends(database.get_db)):
    try:
        return await crud.create_sales_order(db=db, order=order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Order])
async def read_sales_orders(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    return await crud.get_sales_orders(db, skip=skip, limit=limit)

@router.post("/upload")
async def upload_sales_excel(file: UploadFile = File(...), db: AsyncSession = Depends(database.get_db)):
    content = await file.read()
    try:
        # Use the new service that handles parsing and saving with correct column mapping
        result = await import_service.parse_and_save_orders(db, content)
        return {"status": "success", "result": result}
        
    except ValueError as ve:
         # This catches missing columns errors
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@router.put("/{order_id}/items", response_model=schemas.Order)
async def update_order_items(order_id: str, updates: schemas.OrderUpdateItems, db: AsyncSession = Depends(database.get_db)):
    try:
        return await crud.update_sales_order_items(db, order_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/all")
async def delete_all_orders(db: AsyncSession = Depends(database.get_db)):
    try:
        await crud.delete_all_sales_orders(db)
        return {"message": "All sales orders deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

