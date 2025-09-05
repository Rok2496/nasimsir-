from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    specifications: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    stock_quantity: int = 1

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    specifications: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Customer Schemas
class CustomerBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    quantity: int = 1
    special_requirements: Optional[str] = None
    delivery_address: Optional[str] = None

class OrderCreate(OrderBase):
    customer: CustomerCreate
    product_id: int

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    special_requirements: Optional[str] = None
    delivery_address: Optional[str] = None

class Order(OrderBase):
    id: int
    customer_id: int
    product_id: int
    total_price: float
    status: str
    order_date: datetime
    updated_at: Optional[datetime] = None
    customer: Customer
    product: Product
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageCreate(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"

class ChatMessageResponse(BaseModel):
    response: str
    session_id: str

class ChatMessage(BaseModel):
    id: int
    message: str
    response: Optional[str] = None
    language: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatSession(BaseModel):
    id: int
    session_id: str
    created_at: datetime
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True

# Admin Schemas
class AdminBase(BaseModel):
    username: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

class Admin(AdminBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_orders: int
    pending_orders: int
    confirmed_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    total_customers: int
    recent_orders: List[Order]

class OrderSummary(BaseModel):
    id: int
    customer_name: str
    total_price: float
    status: str
    order_date: datetime
    
    class Config:
        from_attributes = True