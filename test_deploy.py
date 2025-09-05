"""
Test script to verify the application can start correctly.
This is useful for CI/CD pipelines and deployment verification.
"""

import os
import sys
from main import app
import uvicorn

def test_app_startup():
    """Test that the FastAPI app can be imported and started"""
    try:
        # Test that the app instance exists
        assert app is not None
        print("✓ FastAPI app instance created successfully")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        assert len(routes) > 0
        print(f"✓ {len(routes)} routes registered")
        
        # Check for critical routes
        critical_routes = ["/", "/health", "/api/products/", "/api/orders/", "/api/chat/"]
        for route in critical_routes:
            assert any(r.startswith(route.split('{')[0]) for r in routes), f"Route {route} not found"
        print("✓ All critical routes registered")
        
        print("✓ All startup tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Startup test failed: {e}")
        return False

if __name__ == "__main__":
    if test_app_startup():
        print("Application is ready for deployment!")
        sys.exit(0)
    else:
        print("Application failed startup tests!")
        sys.exit(1)