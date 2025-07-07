#!/usr/bin/env python3

import asyncio
import aiohttp
import json

async def check_data_structure():
    """Check the actual data structure from Stardust API"""
    
    # First login to get token
    login_url = "https://stardust.my-firstcare.com/auth/login"
    login_data = {
        "username": "operapanel",
        "password": "opera2024"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        async with session.post(login_url, json=login_data) as resp:
            if resp.status != 200:
                print(f"Login failed: {resp.status}")
                return
            
            login_response = await resp.json()
            token = login_response.get("access_token")
            
            if not token:
                print("No token received")
                return
            
            print(f"Got token: {token[:50]}...")
            
            # Test each endpoint
            endpoints = [
                ("provinces", "https://stardust.my-firstcare.com/admin/master-data/provinces"),
                ("districts", "https://stardust.my-firstcare.com/admin/master-data/districts"),
                ("sub_districts", "https://stardust.my-firstcare.com/admin/master-data/sub_districts"),
                ("hospital_types", "https://stardust.my-firstcare.com/admin/master-data/hospital_types"),
                ("hospitals", "https://stardust.my-firstcare.com/admin/master-data/hospitals")
            ]
            
            headers = {"Authorization": f"Bearer {token}"}
            
            for name, url in endpoints:
                print(f"\n=== Testing {name} ===")
                try:
                    async with session.get(url, headers=headers) as resp:
                        print(f"Status: {resp.status}")
                        if resp.status == 200:
                            data = await resp.json()
                            print(f"Response keys: {list(data.keys())}")
                            
                            items = data.get("data", [])
                            if items:
                                print(f"Total items: {len(items)}")
                                print(f"First item structure:")
                                first_item = items[0]
                                print(json.dumps(first_item, indent=2, ensure_ascii=False))
                                
                                # Check name field specifically
                                if "name" in first_item:
                                    name_field = first_item["name"]
                                    print(f"Name field type: {type(name_field)}")
                                    print(f"Name field value: {name_field}")
                        else:
                            text = await resp.text()
                            print(f"Error response: {text}")
                            
                except Exception as e:
                    print(f"Error testing {name}: {e}")

if __name__ == "__main__":
    asyncio.run(check_data_structure())
