from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    sizes = Column(String(200))  # JSON string of available sizes
    stock = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    size = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200), nullable=False)
    shipping_address = Column(Text, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    size = Column(String(10))
    price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

# Pydantic Models
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    sizes: List[str]
    stock: int = 0
    featured: bool = False
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    size: str
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    shipping_address: str

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    shipping_address: str
    total_amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True