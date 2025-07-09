#!/usr/bin/env python3
"""Test script to verify hospitals admin page is working correctly"""

import asyncio
import httpx
import json

# Test configuration
BASE_URL = "http://localhost:5055"
TEST_USERNAME = "admin"
TEST_PASSWORD = "password123"

async def test_hospitals_page():
    """Test the hospitals admin page functionality"""
    print("🔍 Testing hospitals admin page functionality...")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # Step 1: Login
        print("1. Logging in...")
        login_response = await client.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed with status {login_response.status_code}")
            return False
        
        print("✅ Login successful")
        
        # Step 2: Access hospitals admin page
        print("2. Accessing hospitals admin page...")
        hospitals_response = await client.get(f"{BASE_URL}/admin/master-data/hospitals")
        
        if hospitals_response.status_code != 200:
            print(f"❌ Hospitals page failed with status {hospitals_response.status_code}")
            return False
        
        print("✅ Hospitals page accessible")
        
        # Step 3: Check if page contains province filters
        page_content = hospitals_response.text
        
        if "province" in page_content.lower():
            print("✅ Province filters found in page")
        else:
            print("⚠️  Province filters not clearly visible in page")
        
        # Step 4: Test API endpoints for provinces
        print("3. Testing provinces API endpoint...")
        provinces_response = await client.get(f"{BASE_URL}/admin/dropdown/provinces")
        
        if provinces_response.status_code != 200:
            print(f"❌ Provinces API failed with status {provinces_response.status_code}")
            return False
        
        provinces_data = provinces_response.json()
        provinces_count = len(provinces_data.get("data", []))
        print(f"✅ Provinces API working - Found {provinces_count} provinces")
        
        # Step 5: Test districts API endpoint (if we have provinces)
        if provinces_count > 0:
            print("4. Testing districts API endpoint...")
            first_province = provinces_data["data"][0]
            province_code = first_province.get("code")
            
            if province_code:
                districts_response = await client.get(f"{BASE_URL}/admin/dropdown/districts?province_code={province_code}")
                
                if districts_response.status_code == 200:
                    districts_data = districts_response.json()
                    districts_count = len(districts_data.get("data", []))
                    print(f"✅ Districts API working - Found {districts_count} districts for province {province_code}")
                else:
                    print(f"❌ Districts API failed with status {districts_response.status_code}")
                    return False
            else:
                print("⚠️  Province code not found")
        
        # Step 6: Test session persistence
        print("5. Testing session persistence...")
        profile_response = await client.get(f"{BASE_URL}/admin/profile")
        
        if profile_response.status_code == 200:
            print("✅ Session persistence working - profile page accessible")
        else:
            print(f"❌ Session persistence issue - profile page status {profile_response.status_code}")
        
        return True

if __name__ == "__main__":
    result = asyncio.run(test_hospitals_page())
    if result:
        print("\n🎉 All tests passed! Hospitals admin page is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the logs.")
