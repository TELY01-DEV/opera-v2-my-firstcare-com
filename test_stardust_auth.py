#!/usr/bin/env python3
"""
Test script to authenticate with Stardust API and fetch master data
"""
import asyncio
import aiohttp
import json

STARDUST_BASE_URL = "http://localhost:5054"

async def test_stardust_auth():
    """Test authentication and data fetching from Stardust API"""
    async with aiohttp.ClientSession() as session:
        # Test different credentials
        credentials_list = [
            {"username": "operapanel", "password": "operatemppassword"},
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
        ]
        
        token = None
        for creds in credentials_list:
            print(f"\nTrying credentials: {creds['username']}")
            
            # Try to authenticate
            auth_url = f"{STARDUST_BASE_URL}/api/auth/login"
            auth_data = {
                "username": creds["username"],
                "password": creds["password"]
            }
            
            try:
                async with session.post(auth_url, json=auth_data) as response:
                    print(f"Auth response status: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        print(f"Auth response: {json.dumps(result, indent=2)}")
                        if "access_token" in result:
                            token = result["access_token"]
                            print(f"✅ Successfully authenticated with {creds['username']}")
                            break
                    else:
                        text = await response.text()
                        print(f"Auth failed: {text}")
            except Exception as e:
                print(f"Auth error: {e}")
        
        if not token:
            print("❌ Failed to authenticate with any credentials")
            return
        
        # Test provinces endpoint
        print(f"\n🧪 Testing provinces endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try different endpoint variations
        endpoints_to_test = [
            "/api/master-data/provinces",
            "/api/provinces", 
            "/api/admin/provinces",
            "/api/masterdata/provinces"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{STARDUST_BASE_URL}{endpoint}"
                print(f"\nTrying: {url}")
                async with session.get(url, headers=headers) as response:
                    print(f"Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Success! Data structure:")
                        if isinstance(data, dict):
                            print(f"Keys: {list(data.keys())}")
                            if "data" in data and data["data"]:
                                sample = data["data"][0]
                                print(f"Sample record keys: {list(sample.keys()) if isinstance(sample, dict) else type(sample)}")
                                if isinstance(sample, dict) and "name" in sample:
                                    print(f"Name field type: {type(sample['name'])}")
                                    print(f"Name field value: {sample['name']}")
                        break
                    else:
                        text = await response.text()
                        print(f"Error: {text}")
            except Exception as e:
                print(f"Request error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stardust_auth())
