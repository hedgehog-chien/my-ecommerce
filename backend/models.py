from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    weight_g = Column(Integer, default=0)
    current_qty = Column(Integer, default=0)
    avg_cost_twd = Column(Float, default=0.0)

    # Relationships
    purchase_items = relationship("PurchaseItem", back_populates="product")
    sales_items = relationship("SalesItem", back_populates="product")

class PurchaseBatch(Base):
    __tablename__ = "purchase_batches"

    id = Column(String, primary_key=True, default=generate_uuid)
    purchase_date = Column(Date, default=datetime.date.today)
    source = Column(String)
    currency = Column(String, default="JPY")
    
    total_jpy = Column(Integer, default=0)
    total_twd_card_bill = Column(Integer, default=0)
    total_twd_foreign_fee = Column(Integer, default=0)
    total_shipping_twd = Column(Integer, default=0)
    
    exchange_rate = Column(Float, default=0.0)
    shipping_rate_per_g = Column(Float, default=0.0)

    items = relationship("PurchaseItem", back_populates="batch", cascade="all, delete-orphan")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    batch_id = Column(String, ForeignKey("purchase_batches.id"))
    product_id = Column(String, ForeignKey("products.id"))
    
    qty = Column(Integer, default=0)
    unit_price_jpy = Column(Integer, default=0)
    item_weight_g = Column(Integer, default=0) # Snapshot
    final_cost_twd = Column(Float, default=0.0)

    batch = relationship("PurchaseBatch", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")

class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    order_no = Column(String, unique=True, index=True)
    platform_source = Column(String, default="Myship")
    order_date = Column(Date, default=datetime.date.today)
    customer_name = Column(String)
    
    total_amount_received = Column(Integer, default=0)
    shipping_fee_paid_by_customer = Column(Integer, default=0)

    items = relationship("SalesItem", back_populates="order", cascade="all, delete-orphan")

class SalesItem(Base):
    __tablename__ = "sales_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("sales_orders.id"))
    product_id = Column(String, ForeignKey("products.id"))
    
    qty = Column(Integer, default=0)
    unit_price_sold = Column(Integer, default=0)
    historical_cost_basis = Column(Float, default=0.0) # Snapshot of avg_cost

    order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product", back_populates="sales_items")
