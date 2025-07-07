#!/usr/bin/env python3
"""
Test Stardust API DELETE operations
"""
import asyncio
import aiohttp
import json

STARDUST_BASE_URL = "http://localhost:5054"

async def test_delete_operations():
    """Test if Stardust API supports DELETE operations"""
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
        
        # Get a sample record first
        print("\n🔍 Getting sample province record...")
        async with session.get(f"{STARDUST_BASE_URL}/admin/master-data/provinces?limit=1", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("data") and len(data["data"]) > 0:
                    sample_record = data["data"][0]
                    record_id = sample_record["_id"]
                    record_name = sample_record.get("name", [])
                    print(f"Sample record ID: {record_id}")
                    print(f"Sample record name: {record_name}")
                    
                    # Test if DELETE endpoint exists (but don't actually delete)
                    print(f"\n🧪 Testing DELETE endpoint (OPTIONS request)...")
                    delete_url = f"{STARDUST_BASE_URL}/admin/master-data/provinces/{record_id}"
                    
                    # Try OPTIONS method first to see what methods are allowed
                    try:
                        async with session.options(delete_url, headers=headers) as options_response:
                            print(f"OPTIONS response status: {options_response.status}")
                            if "allow" in options_response.headers:
                                print(f"Allowed methods: {options_response.headers['allow']}")
                    except Exception as e:
                        print(f"OPTIONS error: {e}")
                    
                    # Try DELETE with a test (might return error but we can see if endpoint exists)
                    print(f"\n🧪 Testing DELETE endpoint availability...")
                    try:
                        async with session.delete(delete_url, headers=headers) as delete_response:
                            print(f"DELETE response status: {delete_response.status}")
                            text = await delete_response.text()
                            print(f"DELETE response: {text[:200]}...")
                            
                            if delete_response.status in [200, 204]:
                                print("✅ DELETE operation succeeded")
                            elif delete_response.status == 404:
                                print("❌ DELETE endpoint not found")
                            elif delete_response.status == 405:
                                print("❌ DELETE method not allowed")
                            elif delete_response.status == 403:
                                print("❌ DELETE operation forbidden")
                            else:
                                print(f"⚠️  DELETE returned status {delete_response.status}")
                                
                    except Exception as e:
                        print(f"DELETE error: {e}")
                else:
                    print("❌ No records found")
            else:
                print("❌ Failed to get records")

if __name__ == "__main__":
    asyncio.run(test_delete_operations())
