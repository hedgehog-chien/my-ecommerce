from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import database
import models
import schemas

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

@router.get("/stats")
async def get_inventory_stats(db: AsyncSession = Depends(database.get_db)):
    # Total Products
    result_count = await db.execute(select(func.count(models.Product.id)))
    total_products = result_count.scalar()

    # Total Stock Value (Sum of Current Qty * Avg Cost)
    # Note: This is an approximation if using avg_cost
    result_value = await db.execute(select(func.sum(models.Product.current_qty * models.Product.avg_cost_twd)))
    total_value = result_value.scalar() or 0.0

    return {
        "total_active_products": total_products,
        "total_inventory_value_twd": total_value
    }

@router.post("/adjust")
async def adjust_inventory(adjustment: schemas.InventoryAdjustmentCreate, db: AsyncSession = Depends(database.get_db)):
    # Get Product
    result = await db.execute(select(models.Product).filter(models.Product.id == adjustment.product_id))
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update Qty
    if product.current_qty is None:
        product.current_qty = 0
    
    product.current_qty += adjustment.change_qty
    
    # Optional: Log reason to a new table 'InventoryLog' if needed in future
    # for now, just update state
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return {"message": "Inventory updated", "new_qty": product.current_qty}

@router.delete("/clear")
async def clear_all_data(db: AsyncSession = Depends(database.get_db)):
    """
    DANGER: Clears ALL data (Products, Sales, Purchases).
    Use for testing reset.
    """
    import crud
    try:
        await crud.clear_all_data(db)
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
