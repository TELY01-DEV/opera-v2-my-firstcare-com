#!/usr/bin/env python3
"""
Test script to verify the districts API endpoint fix
"""
import asyncio
import aiohttp
import json
import sys

async def test_districts_api():
    """Test the corrected districts API endpoint"""
    
    # Test the corrected API endpoint
    base_url = "http://localhost:5055"
    endpoint = "/api/master-data/districts/11"  # Bangkok province code
    
    print("🔍 Testing Districts API Fix")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # First login to get session cookie
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            print("🔐 Logging in to get session...")
            async with session.post(f"{base_url}/login", data=login_data) as response:
                if response.status != 200:
                    print(f"❌ Login failed with status: {response.status}")
                    return False
                
                print("✅ Login successful")
            
            # Test the districts API endpoint
            print(f"🌐 Testing endpoint: {endpoint}")
            async with session.get(f"{base_url}{endpoint}") as response:
                status = response.status
                content_type = response.headers.get('content-type', '')
                
                print(f"📊 Response Status: {status}")
                print(f"📋 Content-Type: {content_type}")
                
                if status == 200:
                    if 'application/json' in content_type:
                        data = await response.json()
                        print("✅ API endpoint is working!")
                        print(f"📦 Response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        if "data" in data:
                            districts = data["data"]
                            print(f"🏘️  Districts found: {len(districts) if isinstance(districts, list) else 'N/A'}")
                            if districts and len(districts) > 0:
                                print(f"📍 Sample district: {districts[0].get('name', 'N/A')}")
                        
                        return True
                    else:
                        text = await response.text()
                        print(f"❌ Unexpected content type. Response: {text[:200]}...")
                        return False
                elif status == 404:
                    print("❌ 404 Error - Endpoint still not found")
                    return False
                elif status == 401:
                    print("❌ 401 Error - Authentication failed")
                    return False
                else:
                    text = await response.text()
                    print(f"❌ Error {status}: {text[:200]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            return False

async def main():
    print("Districts API Endpoint Test")
    print("=" * 50)
    
    success = await test_districts_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test PASSED: Districts API endpoint is working correctly!")
        print("✅ The 404 error has been resolved.")
    else:
        print("❌ Test FAILED: Districts API endpoint still has issues.")
    
    return 0 if success else 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)
