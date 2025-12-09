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

@router.post("/upload", response_model=List[schemas.Order])
async def upload_sales_excel(file: UploadFile = File(...), db: AsyncSession = Depends(database.get_db)):
    content = await file.read()
    try:
        # 1. Parse Excel
        parsed_data = await import_service.parse_sales_order_excel(content)
        
        # 2. Convert to Schema and Create
        created_orders = []
        
        # Group logic might be needed if multiple rows belong to same order
        # For V1, assuming parse_sales_order_excel returns list of OrderCreate-compatible dicts?
        # Actually import_service returns flat list. We need to group by OrderID.
        
        # Simple grouping logic
        orders_map = {}
        for row in parsed_data:
            order_id = row['platform_order_id']
            if order_id not in orders_map:
                orders_map[order_id] = {
                    "platform_order_id": order_id,
                    "order_date": row.get('order_date'),
                    "customer_name": row.get('customer_name'),
                    "items": []
                }
            
            orders_map[order_id]["items"].append({
                "product_name": row['product_name'],
                "quantity": row['quantity'],
                "unit_price": row['unit_price'],
                "total_price": row['total_price']
            })
            
        for order_dict in orders_map.values():
            order_schema = schemas.OrderCreate(**order_dict)
            try:
                db_order = await crud.create_sales_order(db, order_schema)
                created_orders.append(db_order)
            except Exception as e:
                print(f"Failed to create order {order_dict['platform_order_id']}: {e}")
                # Continue or abort? For now continue
                
        return created_orders
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {str(e)}")
