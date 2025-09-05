from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import os
import shutil
import uuid
from pathlib import Path

from database import get_db
from models import Product as ProductModel, Customer as CustomerModel, Order as OrderModel, ChatSession as ChatSessionModel, ChatMessage as ChatMessageModel, Admin as AdminModel
from schemas import *
from auth import get_current_admin, authenticate_admin, create_access_token, get_password_hash
from services.email_service import EmailService
from services.telegram_service import TelegramService
from services.chatbot_service import ChatbotService
import uuid

# Initialize services
email_service = EmailService()
telegram_service = TelegramService()
chatbot_service = ChatbotService()

# Create routers
product_router = APIRouter(prefix="/api/products", tags=["Products"])
order_router = APIRouter(prefix="/api/orders", tags=["Orders"])
chat_router = APIRouter(prefix="/api/chat", tags=["Chatbot"])
admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
files_router = APIRouter(prefix="/api/admin/files", tags=["File Management"])

# Product Routes
@product_router.get("/", response_model=List[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all active products"""
    products = db.query(ProductModel).filter(ProductModel.is_active == True).offset(skip).limit(limit).all()
    return products

@product_router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@product_router.post("/", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Create a new product (Admin only)"""
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@product_router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Update a product (Admin only)"""
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Order Routes
@order_router.post("/", response_model=Order)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    # Get or create customer
    customer_data = order.customer.dict()
    db_customer = db.query(CustomerModel).filter(CustomerModel.email == customer_data["email"]).first()
    
    if not db_customer:
        db_customer = CustomerModel(**customer_data)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
    
    # Get product
    product = db.query(ProductModel).filter(ProductModel.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate total price
    total_price = product.price * order.quantity
    
    # Create order
    db_order = OrderModel(
        customer_id=db_customer.id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        special_requirements=order.special_requirements,
        delivery_address=order.delivery_address
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Prepare data for notifications
    order_data = {
        "id": db_order.id,
        "product_name": product.name,
        "quantity": db_order.quantity,
        "total_price": db_order.total_price,
        "status": db_order.status,
        "special_requirements": db_order.special_requirements,
        "delivery_address": db_order.delivery_address,
        "order_date": db_order.order_date.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    customer_info = {
        "full_name": db_customer.full_name,
        "email": db_customer.email,
        "phone": db_customer.phone,
        "address": db_customer.address,
        "city": db_customer.city,
        "country": db_customer.country
    }
    
    # Send notifications
    try:
        await email_service.send_order_notification(order_data, customer_info)
        await telegram_service.send_order_notification(order_data, customer_info)
    except Exception as e:
        print(f"Notification error: {e}")
        # Continue even if notifications fail
    
    # Return order with relationships
    db_order.customer = db_customer
    db_order.product = product
    return db_order

@order_router.get("/", response_model=List[Order])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Get all orders (Admin only)"""
    query = db.query(OrderModel)
    
    if status:
        query = query.filter(OrderModel.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@order_router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Get a specific order (Admin only)"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@order_router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Update an order (Admin only)"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@order_router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Delete an order (Admin only)"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    return {"message": f"Order #{order_id} has been successfully deleted"}

# Chat Routes
@chat_router.post("/", response_model=ChatMessageResponse)
async def chat_with_bot(message_data: ChatMessageCreate, db: Session = Depends(get_db)):
    """Chat with the AI assistant"""
    session_id = message_data.session_id or str(uuid.uuid4())
    
    # Get or create chat session
    chat_session = db.query(ChatSessionModel).filter(ChatSessionModel.session_id == session_id).first()
    if not chat_session:
        chat_session = ChatSessionModel(session_id=session_id)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
    
    # Get AI response
    try:
        ai_response = await chatbot_service.get_response(
            message_data.message, 
            message_data.language
        )
        print(f"AI Response: {ai_response}")
    except Exception as e:
        print(f"Error getting AI response: {e}")
        ai_response = "I'm having technical difficulties. Please contact us at 01678-134547."
    
    # Save chat message
    chat_message = ChatMessageModel(
        session_id=session_id,
        message=message_data.message,
        response=ai_response,
        language=message_data.language
    )
    
    db.add(chat_message)
    db.commit()
    
    return ChatMessageResponse(response=ai_response, session_id=session_id)

@chat_router.get("/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.session_id == session_id
    ).order_by(ChatMessageModel.timestamp).all()
    
    return messages

# Admin Routes
@admin_router.post("/login", response_model=Token)
async def login_admin(admin_login: AdminLogin, db: Session = Depends(get_db)):
    """Admin login"""
    admin = authenticate_admin(db, admin_login.username, admin_login.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

@admin_router.post("/register", response_model=Admin)
async def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    """Register new admin (for initial setup)"""
    # Check if admin already exists
    existing_admin = db.query(AdminModel).filter(AdminModel.username == admin.username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(AdminModel).filter(AdminModel.email == admin.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new admin
    hashed_password = get_password_hash(admin.password)
    db_admin = AdminModel(
        username=admin.username,
        email=admin.email,
        hashed_password=hashed_password,
        is_superuser=True  # First admin is superuser
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@admin_router.get("/me", response_model=Admin)
async def get_current_admin_info(current_admin: AdminModel = Depends(get_current_admin)):
    """Get current admin information"""
    return current_admin

# Dashboard Routes
@dashboard_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Get dashboard statistics"""
    # Get order counts by status
    total_orders = db.query(OrderModel).count()
    pending_orders = db.query(OrderModel).filter(OrderModel.status == "pending").count()
    confirmed_orders = db.query(OrderModel).filter(OrderModel.status == "confirmed").count()
    shipped_orders = db.query(OrderModel).filter(OrderModel.status == "shipped").count()
    delivered_orders = db.query(OrderModel).filter(OrderModel.status == "delivered").count()
    cancelled_orders = db.query(OrderModel).filter(OrderModel.status == "cancelled").count()
    
    # Calculate total revenue
    total_revenue = db.query(func.sum(OrderModel.total_price)).filter(
        OrderModel.status.in_(["confirmed", "shipped", "delivered"])
    ).scalar() or 0
    
    # Get total customers
    total_customers = db.query(CustomerModel).count()
    
    # Get recent orders (last 10)
    recent_orders = db.query(OrderModel).order_by(desc(OrderModel.order_date)).limit(10).all()
    
    return DashboardStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        confirmed_orders=confirmed_orders,
        shipped_orders=shipped_orders,
        delivered_orders=delivered_orders,
        cancelled_orders=cancelled_orders,
        total_revenue=float(total_revenue),
        total_customers=total_customers,
        recent_orders=recent_orders
    )

# File Management Routes (Admin Only)
@files_router.post("/upload-image")
async def admin_upload_image(
    file: UploadFile = File(...),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Upload image file (Admin only)"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create upload directory
    upload_dir = Path("static/images")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "url": f"/static/images/{unique_filename}",
        "message": "Image uploaded successfully"
    }

@files_router.post("/upload-video")
async def admin_upload_video(
    file: UploadFile = File(...),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Upload video file (Admin only)"""
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Create upload directory
    upload_dir = Path("static/videos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "url": f"/static/videos/{unique_filename}",
        "message": "Video uploaded successfully"
    }

@files_router.get("/list/{file_type}")
async def list_files(
    file_type: str,
    current_admin: AdminModel = Depends(get_current_admin)
):
    """List all files of specified type (Admin only)"""
    if file_type not in ["images", "videos"]:
        raise HTTPException(status_code=400, detail="File type must be 'images' or 'videos'")
    
    directory = Path(f"static/{file_type}")
    if not directory.exists():
        return {"files": []}
    
    files = []
    for file_path in directory.iterdir():
        if file_path.is_file():
            stat_info = file_path.stat()
            files.append({
                "filename": file_path.name,
                "url": f"/static/{file_type}/{file_path.name}",
                "size": stat_info.st_size,
                "created": stat_info.st_ctime
            })
    
    return {"files": sorted(files, key=lambda x: x['created'], reverse=True)}

@files_router.delete("/delete/{file_type}/{filename}")
async def delete_file(
    file_type: str,
    filename: str,
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Delete a file (Admin only)"""
    if file_type not in ["images", "videos"]:
        raise HTTPException(status_code=400, detail="File type must be 'images' or 'videos'")
    
    file_path = Path(f"static/{file_type}/{filename}")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path.unlink()
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@files_router.put("/update-product-media/{product_id}")
async def update_product_media(
    product_id: int,
    images: List[str] = None,
    video_url: str = None,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    """Update product images and video (Admin only)"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if images is not None:
        product.images = images
    
    if video_url is not None:
        product.video_url = video_url
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Product media updated successfully",
        "product_id": product_id,
        "images": product.images,
        "video_url": product.video_url
    }