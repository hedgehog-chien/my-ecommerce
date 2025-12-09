from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import uuid

# --- Products ---
class ProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    weight_g: int = 0
    cost_price: float = 0.0 # This might be computed or initial
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: str
    current_qty: int
    avg_cost_twd: float

    class Config:
        from_attributes = True

# --- Purchase Items ---
class PurchaseItemBase(BaseModel):
    product_id: str
    qty: int
    unit_price_jpy: int
    item_weight_g: int

class PurchaseItemCreate(PurchaseItemBase):
    pass

class PurchaseItem(PurchaseItemBase):
    id: str
    batch_id: str
    final_cost_twd: float

    class Config:
        from_attributes = True

# --- Purchase Batches ---
class PurchaseBatchBase(BaseModel):
    purchase_date: date
    source: str
    currency: str = "JPY"
    total_jpy: int
    total_twd_card_bill: int
    total_twd_foreign_fee: int
    total_shipping_twd: int

class PurchaseBatchCreate(PurchaseBatchBase):
    items: List[PurchaseItemCreate]

class PurchaseBatch(PurchaseBatchBase):
    id: str
    exchange_rate: float
    shipping_rate_per_g: float
    items: List[PurchaseItem] = []

    class Config:
        from_attributes = True

# --- Sales Orders ---
class OrderItemBase(BaseModel):
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: str
    order_id: str

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    platform_order_id: str
    order_date: date
    customer_name: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: str
    items: List[OrderItem] = []

    class Config:
        from_attributes = True


# --- Inventory Adjustment ---
class InventoryAdjustmentBase(BaseModel):
    product_id: str
    change_qty: int # Positive to add, negative to remove
    reason: Optional[str] = None

class InventoryAdjustmentCreate(InventoryAdjustmentBase):
    pass

class OrderItemUpdate(BaseModel):
    id: str
    quantity: int
    unit_price: int

class OrderUpdateItems(BaseModel):
    items: List[OrderItemUpdate]

