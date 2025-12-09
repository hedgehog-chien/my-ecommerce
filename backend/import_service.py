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
                
                
                # --- Complex Product Parsing Logic ---
                import re
                
                def parse_complex_product_name(raw: str) -> List[Dict]:
                    """
                    Parses strings like:
                    1. "ItemA 26張" -> [{"name": "ItemA", "qty": 26}]
                    2. "ItemA+ItemB" -> [{"name": "ItemA", "qty": 1}, {"name": "ItemB", "qty": 1}]
                    3. "ItemA+ItemB 各1" -> [{"name": "ItemA", "qty": 1}, {"name": "ItemB", "qty": 1}]
                    4. "23A 1盒 23C 1盒" -> [{"name": "23A", "qty": 1}, {"name": "23C", "qty": 1}]
                    5. "23A epick 兩盒" -> [{"name": "23A epick", "qty": 2}]
                    6. "A+B+C Suffix" -> ["A Suffix", "B Suffix", "C Suffix"]
                    7. "Group1 / Group2" -> Parse both
                    """
                    if not raw: return []
                    raw = str(raw).strip()
                    
                    # 0. Split by '/' first (distinct groups)
                    if '/' in raw:
                        major_parts = raw.split('/')
                        results = []
                        for p in major_parts:
                            results.extend(parse_complex_product_name(p))
                        return results

                    # 1. Normalize chinese numbers and units
                    raw = raw.replace("兩", " 2")
                    raw = raw.replace("兩盒", " 2盒").replace("兩個", " 2個").replace("兩張", " 2張")
                    
                    # 2. Check global "Each" (各)
                    default_qty = 1
                    each_match = re.search(r"各(\d+)", raw)
                    if each_match:
                        default_qty = int(each_match.group(1))
                        raw = raw.replace(each_match.group(0), " ") # Remove "各1"
                        
                    # 3. Split by '+'
                    # Logic for "A+B+C Suffix":
                    # If split by +, and the LAST part contains a space, we treat the part after space as strict suffix 
                    # for previous parts that DO NOT have space.
                    parts = [p.strip() for p in raw.split('+') if p.strip()]
                    
                    if len(parts) > 1:
                        last_part = parts[-1]
                        # Check if last part has space 'Name Suffix'
                        # We use strict check: Must have space, and we take everything after first space as suffix
                        if ' ' in last_part:
                            # Split only on first space
                            last_name, suffix = last_part.split(' ', 1)
                            suffix = ' ' + suffix # Keep space for appending
                            
                            # Apply to previous parts if they look like "just names" (no space)
                            new_parts = []
                            for idx, p in enumerate(parts):
                                if idx == len(parts) - 1:
                                    new_parts.append(p) # Last part already has suffix
                                else:
                                    if ' ' not in p:
                                        new_parts.append(p + suffix)
                                    else:
                                        new_parts.append(p)
                            parts = new_parts

                    parsed_items = []
                    
                    for part in parts:
                        # 4. For each part, looks for specific patterns "Name QtyUnit"
                        # Regex: Non-greedy name, space(optional), digits, specific units
                        # We use findall to catch "23A 1盒 23C 1盒" inside one part if no + exists
                        pattern = r"(.+?)\s*(\d+)\s*[盒個張套組支本]"
                        matches = re.findall(pattern, part)
                        
                        if matches:
                            # If we found explicit sub-items
                            for m in matches:
                                n = m[0].strip()
                                q = int(m[1])
                                parsed_items.append({"name": n, "qty": q})
                        else:
                            # No explicit unit pattern found, check simple tail digit "Name 26"
                            simple_match = re.search(r"^(.+?)\s+(\d+)$", part)
                            if simple_match:
                                parsed_items.append({"name": simple_match.group(1).strip(), "qty": int(simple_match.group(2))})
                            else:
                                # Fallback: Whole part is name, use default/each qty
                                parsed_items.append({"name": part, "qty": default_qty})
                                
                    return parsed_items

                # Execute parsing
                parsed_products = parse_complex_product_name(product_name)
                
                # If for some reason nothing parsed, fallback to raw
                if not parsed_products:
                    parsed_products = [{"name": product_name, "qty": 1}]

                # Distribute Price
                # Total line revenue = qty * unit_price
                # We divide this revenue equally among the parsed items (simple heuristic)
                total_line_revenue = qty * unit_price
                num_sub_items = len(parsed_products)
                revenue_per_sub_item = total_line_revenue / num_sub_items if num_sub_items > 0 else 0
                
                for p_info in parsed_products:
                    sub_name = p_info["name"]
                    bundle_qty = p_info["qty"]
                    
                    # Total qty for this sub-product = OrderQty * BundleQty
                    # e.g. Order 2 boxes, each box is "A+B". Then we have 2 A and 2 B.
                    final_qty = qty * bundle_qty
                    
                    # Unit price per atomic item
                    # Total revenue for this chunk = revenue_per_sub_item
                    # Unit price = revenue_per_sub_item / final_qty
                    # Note: Revenue per sub item is for the "Whole Order Line". 
                    # Actually: revenue_per_sub_item is (TotalLine / N). 
                    # If line qty is 2, then we have 2 * BundleQty items.
                    # Price per unit = (TotalLine / N) / (LineQty * BundleQty) NO.
                    # Let's verify:
                    # Line: "A+B", Qty 1, Price 1000. -> A (1), B (1). Rev 1000.
                    # sub_items = 2. rev_per_sub = 500.
                    # A: final_qty = 1*1=1. unit_price = 500/1 = 500.
                    # B: final_qty = 1*1=1. unit_price = 500/1 = 500. Sum = 1000. Correct.
                    
                    # Line: "A 2pcs", Qty 3, Price 100 (Unit 33.33). Total 100.
                    # parsed: A (2). items=1. rev_per_sub = 100.
                    # A: final_qty = 3 * 2 = 6. 
                    # unit_price = 100 / 6 = 16.66.
                    # 6 * 16.66 = 100. Correct.
                    
                    final_unit_price = 0
                    if final_qty > 0:
                        final_unit_price = revenue_per_sub_item / float(bundle_qty) # Wait, logic above says /final_qty?
                        # R = 100. N=1. 
                        # FinalQty = 6. 
                        # UnitPrice = 100 / 6 = 16.66.
                        # Wait, revenue_per_sub_item is TOTAL revenue allocated to this variant in the entire line.
                        # So yes, UnitPrice = AllocatedRevenue / TotalQuantityOfThisVariant
                        final_unit_price = revenue_per_sub_item # This is the "Total for this variant"
                        # We need unit price sold.
                        # Unit Price Sold = (Total Allocated Revenue) / (Line Qty * Bundle Qty) ???
                        # NO. unit_price in DB is "Price of one atomic item".
                        # Yes.
                        # Rev = 100.
                        # final_qty = 6.
                        # atomic_price = 100 / 6 = 16.66.
                        # So atomic_price = revenue_per_sub_item / final_qty ? 
                        # revenue_per_sub_item = 100. final_qty = 6. 100/6 = 16.66.
                        # Correct.
                        
                        # Wait, what if Qty is 0? Avoid div by 0.
                        final_unit_price = revenue_per_sub_item / final_qty

                    # Find or Create Product
                    prod_stmt = select(Product).where(Product.name == sub_name)
                    prod_res = await db.execute(prod_stmt)
                    product = prod_res.scalars().first()
                    
                    if not product:
                        product = Product(name=sub_name)
                        db.add(product)
                        await db.flush()
                        results["created_products"] += 1
                    
                    # Create Sales Item
                    sales_item = SalesItem(
                        order=new_order,
                        product=product,
                        qty=final_qty,
                        unit_price_sold=final_unit_price,
                    )
                    db.add(sales_item)
                    
                    # Deduct Inventory
                    if product.current_qty is None:
                        product.current_qty = 0
                    product.current_qty -= final_qty
                    db.add(product)
            
            new_order.total_amount_received = total_amount
            db.add(new_order)
            results["created_orders"] += 1

        await db.commit()
        return results

    except Exception as e:
        await db.rollback()
        raise e
