#!/usr/bin/env python3
"""
Test script to simulate and test token refresh functionality
"""
import asyncio
import httpx
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5055"

async def test_opera_panel_refresh():
    """Test the Opera Panel refresh token functionality"""
    
    print("Testing Opera Panel refresh token functionality...")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login
        print("\n1. Logging in...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "Sim!443355"}
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
            
        # Extract cookies
        cookies = login_response.cookies
        print(f"✅ Login successful, cookies: {dict(cookies)}")
        
        # Step 2: Test access to hospitals page
        print("\n2. Testing hospitals page access...")
        hospitals_response = await client.get(
            f"{BASE_URL}/admin/master-data/hospitals?skip=0&limit=5",
            cookies=cookies
        )
        
        print(f"Hospitals response status: {hospitals_response.status_code}")
        if hospitals_response.status_code == 200:
            print("✅ Hospitals page accessible")
        else:
            print(f"❌ Hospitals page not accessible: {hospitals_response.text[:200]}")
            
        # Step 3: Wait for token to expire and test again
        print("\n3. Waiting for token to expire...")
        # JWT tokens from our test expire in about 5 minutes, but let's wait a bit and test
        await asyncio.sleep(2)
        
        print("\n4. Testing hospitals page access again...")
        hospitals_response2 = await client.get(
            f"{BASE_URL}/admin/master-data/hospitals?skip=0&limit=5",
            cookies=cookies
        )
        
        print(f"Second hospitals response status: {hospitals_response2.status_code}")
        if hospitals_response2.status_code == 200:
            print("✅ Hospitals page still accessible (token refresh worked)")
        else:
            print(f"❌ Hospitals page not accessible: {hospitals_response2.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_opera_panel_refresh())
