from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import models
import schemas
import uuid

# --- Product CRUD ---
async def get_product(db: AsyncSession, product_id: str):
    result = await db.execute(select(models.Product).filter(models.Product.id == product_id))
    return result.scalars().first()

async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Product).offset(skip).limit(limit))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: schemas.ProductCreate):
    db_product = models.Product(
        sku=product.sku,
        name=product.name,
        weight_g=product.weight_g,
        current_qty=product.stock_quantity, # Initial stock
        avg_cost_twd=product.cost_price     # Initial cost
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# --- Purchase CRUD ---
async def create_purchase_batch(db: AsyncSession, batch: schemas.PurchaseBatchCreate):
    # 1. Calculate Batch Level Rates
    # Exchange Rate = (Card Bill + Fee) / Total JPY
    exchange_rate = 0.0
    if batch.total_jpy > 0:
        exchange_rate = (batch.total_twd_card_bill + batch.total_twd_foreign_fee) / batch.total_jpy
    
    # Calculate Total Weight for Shipping Rate
    total_weight = sum(item.item_weight_g * item.qty for item in batch.items)
    
    # Shipping Rate per Gram = Total Shipping / Total Weight
    shipping_rate_per_g = 0.0
    if total_weight > 0:
        shipping_rate_per_g = batch.total_shipping_twd / total_weight

    # 2. Create Batch Record
    db_batch = models.PurchaseBatch(
        purchase_date=batch.purchase_date,
        source=batch.source,
        currency=batch.currency,
        total_jpy=batch.total_jpy,
        total_twd_card_bill=batch.total_twd_card_bill,
        total_twd_foreign_fee=batch.total_twd_foreign_fee,
        total_shipping_twd=batch.total_shipping_twd,
        exchange_rate=exchange_rate,
        shipping_rate_per_g=shipping_rate_per_g
    )
    db.add(db_batch)
    await db.flush() # Get ID

    # 3. Process Items & Update Inventory/Cost
    for item_data in batch.items:
        # Calculate Final Cost TWD for this item
        # Cost = (Unit Price JPY * ExRate) + (Weight * Shipping Rate)
        item_base_cost = item_data.unit_price_jpy * exchange_rate
        item_shipping_cost = item_data.item_weight_g * shipping_rate_per_g
        final_cost_twd = item_base_cost + item_shipping_cost

        db_item = models.PurchaseItem(
            batch_id=db_batch.id,
            product_id=item_data.product_id,
            qty=item_data.qty,
            unit_price_jpy=item_data.unit_price_jpy,
            item_weight_g=item_data.item_weight_g,
            final_cost_twd=final_cost_twd
        )
        db.add(db_item)

        # 4. Update Product Inventory & Weighted Average Cost
        product = await get_product(db, item_data.product_id)
        if product:
            old_qty = product.current_qty or 0
            old_avg_cost = product.avg_cost_twd or 0.0
            new_qty = item_data.qty
            
            # Weighted Average Formula
            # New Avg = ((Old Qty * Old Avg) + (New Qty * New Unit Cost)) / (Old Qty + New Qty)
            total_old_value = old_qty * old_avg_cost
            total_new_value = new_qty * final_cost_twd
            
            if (old_qty + new_qty) > 0:
                new_avg_cost = (total_old_value + total_new_value) / (old_qty + new_qty)
                product.avg_cost_twd = new_avg_cost
            
            product.current_qty = old_qty + new_qty
            # Update weight to latest if needed, or keep average? Let's update to latest known weight
            if item_data.item_weight_g > 0:
                product.weight_g = item_data.item_weight_g
                
            db.add(product)

    await db.commit()
    await db.refresh(db_batch)
    return db_batch

async def get_purchase_batches(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.PurchaseBatch)
        .options(selectinload(models.PurchaseBatch.items))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# --- Sales CRUD ---
async def create_sales_order(db: AsyncSession, order: schemas.OrderCreate):
    # 1. Create Order Record
    db_order = models.SalesOrder(
        order_no=order.platform_order_id,
        platform_source="Myship", # Defaulting for now
        order_date=order.order_date,
        customer_name=order.customer_name,
        # total_amount_received and shipping_fee logic could be added here if passed in schema
    )
    db.add(db_order)
    await db.flush()

    # 2. Process Items
    for item_data in order.items:
        # Find Product by Name or SKU (Logic allows Fuzzy Match later, strict for now)
        # We assume the schema passed product_name, but we ideally need product_id.
        # For this stage, let's assume the frontend/parser resolves the Product ID or we look it up by name.
        
        # Look up product by name since Excel usually has names
        result = await db.execute(select(models.Product).filter(models.Product.name == item_data.product_name))
        product = result.scalars().first()
        
        if not product:
            # If product not found, we might create a placeholder or error. 
            # For strict inventory, we error.
            raise ValueError(f"Product not found: {item_data.product_name}")

        # Snapshot current stats
        historical_cost = product.avg_cost_twd
        
        db_item = models.SalesItem(
            order_id=db_order.id,
            product_id=product.id,
            qty=item_data.quantity,
            unit_price_sold=item_data.unit_price,
            historical_cost_basis=historical_cost
        )
        db.add(db_item)

        # 3. Deduct Inventory
        if product.current_qty is not None:
            product.current_qty -= item_data.quantity
        db.add(product)

    await db.commit()
    await db.refresh(db_order)
    return db_order

async def get_sales_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.SalesOrder)
        .options(
            selectinload(models.SalesOrder.items).selectinload(models.SalesItem.product)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def delete_all_sales_orders(db: AsyncSession):
    # Depending on cascade rules, deleting orders might autoflush items.
    # explicit delete of items first is safer if cascade isn't set up perfectly.
    await db.execute(models.SalesItem.__table__.delete())
    await db.execute(models.SalesOrder.__table__.delete())
    await db.commit()


