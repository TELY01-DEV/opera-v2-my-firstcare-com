#!/usr/bin/env python3
"""
Test Stardust API with correct endpoints
"""
import asyncio
import aiohttp
import json

STARDUST_BASE_URL = "http://localhost:5054"

async def test_stardust_correct_endpoints():
    """Test Stardust API with correct endpoints"""
    async with aiohttp.ClientSession() as session:
        # Test different login endpoints and credentials
        credentials_list = [
            {"username": "operapanel", "password": "Sim!443355"},
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
        ]
        
        login_endpoints = ["/auth/simple-login", "/auth/login"]
        
        token = None
        
        for endpoint in login_endpoints:
            print(f"\n🧪 Testing {endpoint}")
            for creds in credentials_list:
                print(f"  Trying credentials: {creds['username']}")
                
                try:
                    auth_url = f"{STARDUST_BASE_URL}{endpoint}"
                    async with session.post(auth_url, json=creds) as response:
                        print(f"    Status: {response.status}")
                        if response.status == 200:
                            result = await response.json()
                            print(f"    ✅ Success! Response keys: {list(result.keys())}")
                            if "access_token" in result:
                                token = result["access_token"]
                                print(f"    Got token: {token[:20]}...")
                                break
                            elif "token" in result:
                                token = result["token"]
                                print(f"    Got token: {token[:20]}...")
                                break
                        else:
                            text = await response.text()
                            print(f"    Failed: {text[:100]}...")
                except Exception as e:
                    print(f"    Error: {e}")
            
            if token:
                break
        
        if not token:
            print("\n❌ Failed to authenticate with any credentials")
            print("Let's try to access endpoints without authentication...")
            
            # Try without auth
            test_endpoints = [
                "/admin/master-data/provinces",
                "/admin/master-data/districts",
                "/admin/master-data/hospital-types",
            ]
            
            for endpoint in test_endpoints:
                try:
                    url = f"{STARDUST_BASE_URL}{endpoint}"
                    print(f"\n🧪 Testing {url} (no auth)")
                    async with session.get(url) as response:
                        print(f"Status: {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Success! Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            if isinstance(data, dict) and "data" in data:
                                records = data["data"]
                                if records:
                                    sample = records[0]
                                    print(f"Sample record: {json.dumps(sample, indent=2)[:300]}...")
                            break
                        else:
                            text = await response.text()
                            print(f"Failed: {text[:100]}...")
                except Exception as e:
                    print(f"Error: {e}")
            return
            
        # Test master data endpoints with authentication
        print(f"\n🔍 Testing master data endpoints with token...")
        headers = {"Authorization": f"Bearer {token}"}
        
        test_endpoints = [
            "/admin/master-data/provinces",
            "/admin/master-data/districts", 
            "/admin/master-data/sub-districts",
            "/admin/master-data/hospital-types",
            "/admin/master-data/hospitals",
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f"{STARDUST_BASE_URL}{endpoint}"
                print(f"\n🧪 Testing {url}")
                async with session.get(url, headers=headers) as response:
                    print(f"Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Success! Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        if isinstance(data, dict) and "data" in data:
                            records = data["data"]
                            print(f"Record count: {len(records) if records else 0}")
                            if records:
                                sample = records[0]
                                print(f"Sample record keys: {list(sample.keys()) if isinstance(sample, dict) else type(sample)}")
                                if isinstance(sample, dict) and "name" in sample:
                                    print(f"Name field structure: {sample['name']}")
                    else:
                        text = await response.text()
                        print(f"Failed: {text[:100]}...")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stardust_correct_endpoints())
