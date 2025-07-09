#!/usr/bin/env python3
"""
Test script to verify refresh token functionality
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "https://stardust.my-firstcare.com"

async def test_refresh_token():
    """Test the refresh token functionality"""
    
    # First, login to get tokens
    print("1. Testing login...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "Sim!443355"}
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            return
        
        login_data = login_response.json()
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]
        
        print(f"✅ Login successful")
        print(f"Access token: {access_token[:30]}...")
        print(f"Refresh token: {refresh_token[:30]}...")
        
        # Test access token
        print("\n2. Testing access token...")
        me_response = await client.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"✅ Access token works: {user_data['data']['username']}")
        else:
            print(f"❌ Access token failed: {me_response.status_code}")
        
        # Test refresh token
        print("\n3. Testing refresh token...")
        refresh_response = await client.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        if refresh_response.status_code == 200:
            refresh_data = refresh_response.json()
            new_access_token = refresh_data["access_token"]
            print(f"✅ Refresh token works")
            print(f"New access token: {new_access_token[:30]}...")
            
            # Test new access token
            print("\n4. Testing new access token...")
            new_me_response = await client.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {new_access_token}"}
            )
            
            if new_me_response.status_code == 200:
                print(f"✅ New access token works")
            else:
                print(f"❌ New access token failed: {new_me_response.status_code}")
        else:
            print(f"❌ Refresh token failed: {refresh_response.status_code}")
            print(f"Response: {refresh_response.text}")

if __name__ == "__main__":
    asyncio.run(test_refresh_token())
