import pandas as pd
from io import BytesIO
from typing import List, Dict
from datetime import datetime

# TODO: IMPORTANT - Update these keys to match the EXACT headers in the Maihuobian Excel file
# The value should match the internal field names used in our logic
COLUMN_MAPPING = {
    # "Excel Header Name": "internal_field_name"
    "订单编号": "platform_order_id",         # Example: Order No.
    "商品名称": "product_name",             # Example: Product Name
    "数量": "quantity",                     # Example: Quantity
    "单价": "unit_price",                   # Example: Unit Price
    "总价": "total_price",                  # Example: Total Price
    "下单时间": "order_date",                 # Example: Order Date
    "买家姓名": "customer_name",            # Example: Buyer Name
}

async def parse_sales_order_excel(file_content: bytes) -> List[Dict]:
    """
    Parses the Maihuobian sales order Excel file.
    """
    try:
        # Read Excel file
        df = pd.read_excel(BytesIO(file_content))
        
        parsed_orders = []
        
        # Validate that required columns exist (optional but recommended)
        # for col in COLUMN_MAPPING.keys():
        #     if col not in df.columns:
        #         raise ValueError(f"Missing required column: {col}")

        # Iterate through rows
        for index, row in df.iterrows():
            order_data = {}
            for excel_col, internal_field in COLUMN_MAPPING.items():
                if excel_col in df.columns:
                    val = row[excel_col]
                    # Basic cleaning
                    if pd.isna(val):
                        val = None
                    order_data[internal_field] = val
            
            # Additional processing/cleaning can go here
            # e.g., converting date strings to datetime objects
             
            if order_data.get("platform_order_id"): # Only add if we have an ID
                parsed_orders.append(order_data)
                
        return parsed_orders

    except Exception as e:
        print(f"Error parsing Excel: {e}")
        raise e
