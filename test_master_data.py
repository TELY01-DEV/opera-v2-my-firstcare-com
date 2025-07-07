#!/usr/bin/env python3
"""
Test script for Master Data functionality
"""
import requests
import json

BASE_URL = "http://localhost:5055"

def test_login():
    """Test login with provided credentials"""
    print("Testing login...")
    
    # First get the login page to establish session
    session = requests.Session()
    login_page = session.get(f"{BASE_URL}/login")
    print(f"Login page status: {login_page.status_code}")
    
    # Attempt login
    login_data = {
        "username": "operapanel",
        "password": "Sim!443355"
    }
    
    login_response = session.post(f"{BASE_URL}/auth/login", json=login_data, allow_redirects=False)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response headers: {dict(login_response.headers)}")
    
    if login_response.status_code in [200, 302, 303]:
        print("✅ Login successful")
        return session
    else:
        print(f"❌ Login failed: {login_response.text}")
        return None

def test_master_data_access(session):
    """Test master data access"""
    print("\nTesting master data access...")
    
    # Test master data index
    index_response = session.get(f"{BASE_URL}/admin/master-data", allow_redirects=False)
    print(f"Master data index status: {index_response.status_code}")
    
    if index_response.status_code == 200:
        print("✅ Master data index accessible")
        return True
    elif index_response.status_code in [302, 303]:
        print(f"🔄 Redirected to: {index_response.headers.get('Location', 'unknown')}")
        return False
    else:
        print(f"❌ Master data access failed: {index_response.status_code}")
        return False

def test_master_data_lists(session):
    """Test master data list pages"""
    print("\nTesting master data lists...")
    
    data_types = ["provinces", "districts", "sub-districts", "hospital-types", "hospitals"]
    
    for data_type in data_types:
        response = session.get(f"{BASE_URL}/admin/master-data/{data_type}")
        print(f"  {data_type}: {response.status_code}")
        
        if response.status_code == 200:
            print(f"    ✅ {data_type} list accessible")
        else:
            print(f"    ❌ {data_type} list failed")

def main():
    """Main test function"""
    print("=== Master Data Functionality Test ===\n")
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health check: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test login
    session = test_login()
    if not session:
        return
    
    # Test master data access
    if test_master_data_access(session):
        test_master_data_lists(session)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
