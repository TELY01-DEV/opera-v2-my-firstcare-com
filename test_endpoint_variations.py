#!/usr/bin/env python3
"""
Test different endpoint variations for the failing endpoints
"""
import asyncio
import aiohttp
import json

STARDUST_BASE_URL = "http://localhost:5054"

async def test_endpoint_variations():
    """Test different endpoint variations"""
    async with aiohttp.ClientSession() as session:
        # First authenticate
        auth_url = f"{STARDUST_BASE_URL}/auth/login"
        creds = {"username": "operapanel", "password": "Sim!443355"}
        
        async with session.post(auth_url, json=creds) as response:
            if response.status != 200:
                print("❌ Authentication failed")
                return
            
            result = await response.json()
            token = result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
        print("✅ Authenticated successfully")
        
        # Test different variations for sub-districts
        print("\n🧪 Testing sub-districts endpoint variations:")
        sub_district_endpoints = [
            "/admin/master-data/sub-districts",
            "/admin/master-data/sub_districts", 
            "/admin/master-data/subdistricts",
            "/admin/master-data/sub-district",
            "/admin/master-data/tambon",
            "/admin/master-data/tambons",
        ]
        
        for endpoint in sub_district_endpoints:
            try:
                url = f"{STARDUST_BASE_URL}{endpoint}"
                async with session.get(url, headers=headers) as response:
                    print(f"  {endpoint:<35} Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict) and "data" in data:
                            print(f"    ✅ Success! Record count: {len(data['data'])}")
                        break
                    elif response.status != 404:
                        text = await response.text()
                        print(f"    Error: {text[:50]}...")
            except Exception as e:
                print(f"    Exception: {e}")
        
        # Test different variations for hospital-types
        print("\n🧪 Testing hospital-types endpoint variations:")
        hospital_type_endpoints = [
            "/admin/master-data/hospital-types",
            "/admin/master-data/hospital_types",
            "/admin/master-data/hospitaltypes", 
            "/admin/master-data/hospital-type",
            "/admin/master-data/hospital_categories",
            "/admin/master-data/hospital-categories",
        ]
        
        for endpoint in hospital_type_endpoints:
            try:
                url = f"{STARDUST_BASE_URL}{endpoint}"
                async with session.get(url, headers=headers) as response:
                    print(f"  {endpoint:<35} Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict) and "data" in data:
                            print(f"    ✅ Success! Record count: {len(data['data'])}")
                        break
                    elif response.status != 404:
                        text = await response.text()
                        print(f"    Error: {text[:50]}...")
            except Exception as e:
                print(f"    Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint_variations())
