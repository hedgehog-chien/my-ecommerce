from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import database
import models

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
