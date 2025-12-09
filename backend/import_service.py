import pandas as pd
from io import BytesIO
from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import SalesOrder, SalesItem, Product

# Traditional Chinese Headers for Maihuobian (賣貨便)
# Based on common export formats:
COLUMN_MAPPING = {
    "訂單編號": "order_no",
    "商品名稱": "product_name",
    "數量": "qty",
    "單價": "unit_price",
    "訂單日期": "order_date",
    "買家會員名稱": "customer_name", # Sometimes just 買家, needs verification from user file, but this is a good guess
    # "小計": "subtotal" 
}

async def parse_and_save_orders(db: AsyncSession, file_content: bytes) -> Dict:
    """
    Parses the Excel file and saves orders to the database.
    Returns a summary of actions.
    """
    try:
        # 1. Read Excel (Read without header first to find the correct row)
        # Maihuobian exports often have metadata rows at the top.
        df_raw = pd.read_excel(BytesIO(file_content), header=None)
        
        # Find the row that contains "訂單編號"
        header_row_index = -1
        for i, row in df_raw.head(10).iterrows():
            # Check if any cell in this row contains the key column
            if row.astype(str).str.contains("訂單編號").any():
                header_row_index = i
                break
        
        if header_row_index == -1:
             # Fallback: maybe it is simplified "订单编号"
            for i, row in df_raw.head(10).iterrows():
                if row.astype(str).str.contains("订单编号").any():
                    header_row_index = i
                    break
        
        if header_row_index == -1:
             raise ValueError("Could not find header row containing '訂單編號' in the first 10 rows.")

        # Reload with correct header
        # Note: 'header' in read_excel is 0-indexed. 
        # If we found it at index i, that's the row we want as header.
        df = pd.read_excel(BytesIO(file_content), header=header_row_index)
        
        # 2. Normalize Headers (strip whitespace)
        df.columns = df.columns.str.strip()
        print(f"DEBUG: Found columns in Excel: {df.columns.tolist()}")
        
        # 3. Verify Columns (Check at least Order No exists)
        if "訂單編號" not in df.columns:
             # Fallback check for Simplified Chinese just in case
            if "订单编号" in df.columns:
                 # Remap simplified keys if needed, but assuming user said "Attachment is example of Maihuobian" which is Taiwan-based.
                 pass
            else:
                 # List what we found to help debug
                 raise ValueError(f"Required column '訂單編號' not found. Found columns: {list(df.columns)}")

        # 4. Group by Order ID
        # One order might have multiple rows (items)
        grouped = df.groupby("訂單編號")
        
        results = {
            "created_orders": 0,
            "skipped_orders": 0,
            "created_products": 0,
            "errors": []
        }

        for order_no, group in grouped:
            order_no = str(order_no).strip()
            
            # Check if order exists
            stmt = select(SalesOrder).where(SalesOrder.order_no == order_no)
            result = await db.execute(stmt)
            existing_order = result.scalars().first()
            
            if existing_order:
                results["skipped_orders"] += 1
                continue
            
            # Get Order details from the first row of the group
            first_row = group.iloc[0]
            
            # Parse Date
            order_date_raw = first_row.get("訂單日期")
            order_date = None
            if pd.notna(order_date_raw):
                try:
                    order_date = pd.to_datetime(order_date_raw).date()
                except:
                    order_date = datetime.now().date() # Fallback

            # Create Order
            new_order = SalesOrder(
                order_no=order_no,
                order_date=order_date,
                customer_name=str(first_row.get("買家會員名稱", "")),
                platform_source="Maihuobian"
            )
            
            # Calculate totals based on items
            total_amount = 0
            
            for _, item_row in group.iterrows():
                # Logic updated per user request: 
                # Check "商品名稱(品名/規格)" first, then "賣場名稱", then generic "商品名稱"
                raw_product_name = None
                
                # Try specific columns
                for col_candidate in ["商品名稱(品名/規格)", "賣場名稱", "商品名稱"]:
                    if col_candidate in df.columns:
                        val = item_row.get(col_candidate)
                        if pd.notna(val) and str(val).strip():
                            raw_product_name = str(val).strip()
                            break
                            
                product_name = raw_product_name if raw_product_name else "Unknown Product"
                
                # Helper to clean numbers strings like "1,180"
                def clean_number(val):
                    if pd.isna(val): return 0
                    if isinstance(val, (int, float)): return val
                    return float(str(val).replace(',', '').strip())

                qty = int(clean_number(item_row.get("數量", 0)))
                unit_price = float(clean_number(item_row.get("單價", 0)))
                
                # Find or Create Product
                # Use name as key for now. 
                # Ideally we should use SKU if available in columns like "商品規格" or "商品料號"
                prod_stmt = select(Product).where(Product.name == product_name)
                prod_res = await db.execute(prod_stmt)
                product = prod_res.scalars().first()
                
                if not product:
                    product = Product(name=product_name)
                    db.add(product)
                    await db.flush() # Flush to get ID
                    results["created_products"] += 1
                
                # Create Sales Item
                sales_item = SalesItem(
                    order=new_order,
                    product=product,
                    qty=qty,
                    unit_price_sold=unit_price,
                    # historical_cost_basis could be filled if we had cost info
                )
                db.add(sales_item)
                
                total_amount += (qty * unit_price)
            
                # Deduct Inventory
                if product.current_qty is None:
                     product.current_qty = 0
                product.current_qty -= qty
                db.add(product)
            
            new_order.total_amount_received = total_amount
            db.add(new_order)
            results["created_orders"] += 1

        await db.commit()
        return results

    except Exception as e:
        await db.rollback()
        raise e
