#!/usr/bin/env python3
"""
Database initialization script for SmartTech E-commerce
This script creates the initial product data and admin user
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Product, Admin
from auth import get_password_hash
import json

def init_database():
    """Initialize database with sample data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if product already exists
        existing_product = db.query(Product).first()
        if not existing_product:
            # Create the SmartTech Interactive Smart Board product
            product_data = {
                "name": "SmartTech Interactive Smart Board RK3588",
                "description": """
The SmartTech Interactive Smart Board RK3588 is a cutting-edge educational and business solution 
that combines advanced technology with intuitive design. Perfect for classrooms, meeting rooms, 
and collaborative spaces, this interactive display revolutionizes the way we teach, learn, and present.

Key Features:
- High-performance RK3588 processor for smooth operation
- Crystal-clear 4K display with multi-touch capabilities
- Advanced AI-powered features for enhanced interaction
- Comprehensive connectivity options for all your devices
- Durable construction built for intensive daily use

Transform your space with the future of interactive technology!
                """.strip(),
                "price": 2500.00,  # Base price, contact for final pricing
                "specifications": {
                    "processor": "RK3588",
                    "operating_system": "Android 12",
                    "ram": "16GB",
                    "storage": "256GB",
                    "camera": "48MP AI camera with facial recognition",
                    "microphones": "8 microphones array",
                    "audio": "2.1 channel audio system",
                    "connectivity": ["NFC", "WiFi 6", "Bluetooth 5.2", "USB 3.0", "USB-C", "HDMI"],
                    "security": ["Fingerprint scanner", "Facial recognition"],
                    "sizes_available": ["65 inch", "75 inch", "86 inch", "98 inch", "100 inch", "105 inch", "110 inch"],
                    "resolution": "4K UHD",
                    "touch_points": "20-point multi-touch",
                    "warranty": "2 years international warranty"
                },
                "images": [
                    "/static/images/536276365_4303567749871222_4748269724601006136_n.jpg",
                    "/static/images/540678420_4314079595486704_7084564713675819418_n.jpg",
                    "/static/images/540733563_4313400338887963_1327274053790520535_n.jpg"
                ],
                "video_url": "/static/videos/FDownloader.Net_AQOJAiLv3iA-XM_aTNDjIoNm8fzQx4jijYNCILkeMOUzNi7xHbqU8s_v-sIJ0xhK0ky6hKcBxmX-yhhMFuZ5EEQkSOmpHV3dHMP7m_r9EeO4gQ_720p_(HD).mp4",
                "stock_quantity": 50,
                "is_active": True
            }
            
            product = Product(**product_data)
            db.add(product)
            print("✅ Created SmartTech Interactive Smart Board product")
        
        # Check if admin user exists
        existing_admin = db.query(Admin).first()
        if not existing_admin:
            # Create default admin user
            admin_data = {
                "username": "admin",
                "email": "admin@smarttech.com",
                "hashed_password": get_password_hash("admin123"),
                "is_active": True,
                "is_superuser": True
            }
            
            admin = Admin(**admin_data)
            db.add(admin)
            print("✅ Created default admin user")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  Please change the password after first login!")
        
        # Commit changes
        db.commit()
        print("✅ Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing SmartTech E-commerce Database...")
    init_database()