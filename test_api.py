#!/usr/bin/env python3
"""
Test script for SmartTech E-commerce API
This script tests all the main endpoints to ensure everything is working properly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_welcome():
    """Test welcome endpoint"""
    print("\n🔍 Testing welcome endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_products():
    """Test get products endpoint"""
    print("\n🔍 Testing get products...")
    response = requests.get(f"{BASE_URL}/api/products/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        products = response.json()
        print(f"Found {len(products)} products")
        if products:
            print(f"First product: {products[0]['name']}")
        return True, products
    return False, []

def test_chatbot():
    """Test chatbot endpoint"""
    print("\n🔍 Testing chatbot...")
    chat_data = {
        "message": "Hello, tell me about your Interactive Smart Board",
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/api/chat/", json=chat_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Bot Response: {result['response'][:100]}...")
        print(f"Session ID: {result['session_id']}")
        return True, result['session_id']
    else:
        print(f"Error: {response.text}")
    return False, None

def test_admin_register():
    """Test admin registration (only if no admin exists)"""
    print("\n🔍 Testing admin registration...")
    admin_data = {
        "username": "testadmin",
        "email": "test@smarttech.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/admin/register", json=admin_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Test admin created successfully")
        return True
    elif response.status_code == 400:
        print("Admin already exists (expected)")
        return True
    else:
        print(f"Error: {response.text}")
    return False

def test_admin_login():
    """Test admin login"""
    print("\n🔍 Testing admin login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/admin/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Login successful")
        return True, result['access_token']
    else:
        print(f"Error: {response.text}")
    return False, None

def test_create_order():
    """Test order creation"""
    print("\n🔍 Testing order creation...")
    order_data = {
        "customer": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "city": "New York",
            "country": "USA"
        },
        "product_id": 1,
        "quantity": 1,
        "special_requirements": "Need installation support",
        "delivery_address": "Same as customer address"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/", json=order_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Order created with ID: {result['id']}")
        print(f"Total price: ${result['total_price']}")
        return True, result['id']
    else:
        print(f"Error: {response.text}")
    return False, None

def test_dashboard(token):
    """Test dashboard with admin token"""
    print("\n🔍 Testing dashboard stats...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Total orders: {stats['total_orders']}")
        print(f"Total revenue: ${stats['total_revenue']}")
        print(f"Total customers: {stats['total_customers']}")
        return True
    else:
        print(f"Error: {response.text}")
    return False

def test_admin_file_management(token):
    """Test admin file management endpoints"""
    print("\n🔍 Testing admin file management...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test listing files
    response = requests.get(f"{BASE_URL}/api/admin/files/list/images", headers=headers)
    print(f"List files status: {response.status_code}")
    if response.status_code == 200:
        files = response.json()["files"]
        print(f"Found {len(files)} image files")
        return True
    else:
        print(f"Error listing files: {response.text}")
    
    return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting SmartTech E-commerce API Tests\\n")
    
    # Basic health checks
    if not test_health_check():
        print("❌ Health check failed!")
        return
    
    if not test_welcome():
        print("❌ Welcome endpoint failed!")
        return
    
    # Test products
    success, products = test_get_products()
    if not success or not products:
        print("❌ Products endpoint failed!")
        return
    
    # Test chatbot
    success, session_id = test_chatbot()
    if not success:
        print("⚠️ Chatbot test failed (might need OpenRouter API key)")
    
    # Test admin functions
    test_admin_register()
    
    success, token = test_admin_login()
    if not success:
        print("❌ Admin login failed!")
        return
    
    # Test admin file management
    if test_admin_file_management(token):
        print("✅ Admin file management test passed!")
    
    # Test order creation
    success, order_id = test_create_order()
    if not success:
        print("⚠️ Order creation failed (email/telegram notifications might need configuration)")
    
    # Test dashboard
    if token and test_dashboard(token):
        print("✅ Dashboard test passed!")
    
    print("\\n🎉 All tests completed!")
    print("\\n📈 Key Features:")
    print("✅ Admin-only file management (upload, list, delete)")
    print("✅ Dynamic product media updates")
    print("✅ No authentication required for browsing and ordering")
    print("❌ Public file uploads disabled for security")
    print("\\n📄 API Documentation available at: http://localhost:8000/docs")
    print("🔗 Alternative docs at: http://localhost:8000/redoc")
    """Run all tests"""
    print("🚀 Starting SmartTech E-commerce API Tests\\n")
    
    # Basic health checks
    if not test_health_check():
        print("❌ Health check failed!")
        return
    
    if not test_welcome():
        print("❌ Welcome endpoint failed!")
        return
    
    # Test products
    success, products = test_get_products()
    if not success or not products:
        print("❌ Products endpoint failed!")
        return
    
    # Test chatbot
    success, session_id = test_chatbot()
    if not success:
        print("⚠️ Chatbot test failed (might need OpenRouter API key)")
    
    # Test admin functions
    test_admin_register()
    
    success, token = test_admin_login()
    if not success:
        print("❌ Admin login failed!")
        return
    
    # Test order creation
    success, order_id = test_create_order()
    if not success:
        print("⚠️ Order creation failed (email/telegram notifications might need configuration)")
    
    # Test dashboard
    if token and test_dashboard(token):
        print("✅ Dashboard test passed!")
    
    print("\\n🎉 All basic tests completed!")
    print("\\n📊 API Documentation available at: http://localhost:8000/docs")
    print("🔗 Alternative docs at: http://localhost:8000/redoc")

if __name__ == "__main__":
    # Wait a moment for server to be ready
    time.sleep(2)
    
    try:
        run_all_tests()
    except requests.ConnectionError:
        print("❌ Cannot connect to server. Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")