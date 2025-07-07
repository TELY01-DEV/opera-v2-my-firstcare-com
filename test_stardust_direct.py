#!/usr/bin/env python3
"""
Test authentication with the local Stardust API
"""
import asyncio
import aiohttp
import json

async def test_stardust_direct():
    """Test Stardust API directly"""
    async with aiohttp.ClientSession() as session:
        # Try to access the Stardust API docs to see available endpoints
        base_url = "http://localhost:5054"
        
        print("🔍 Checking Stardust API endpoints...")
        
        # Try different auth endpoints
        auth_endpoints = [
            "/auth/login",
            "/api/auth/login", 
            "/login",
            "/api/login"
        ]
        
        for endpoint in auth_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"\n🧪 Testing: {url}")
                
                # Try POST with different credential sets
                credentials = [
                    {"username": "admin", "password": "admin"},
                    {"username": "opera", "password": "opera"},
                    {"username": "operapanel", "password": "operatemppassword"},
                    {"username": "test", "password": "test"},
                ]
                
                for creds in credentials:
                    async with session.post(url, json=creds) as response:
                        print(f"  {creds['username']}:{creds['password']} -> {response.status}")
                        if response.status in [200, 201]:
                            result = await response.json()
                            print(f"  ✅ Success: {json.dumps(result, indent=2)}")
                            return True
                        elif response.status == 422:
                            error = await response.json()
                            print(f"  🔍 Validation error: {error}")
                        elif response.status == 404:
                            print("  ❌ Endpoint not found")
                            break
                        else:
                            error = await response.text()
                            print(f"  ❌ Error: {error}")
                            
            except Exception as e:
                print(f"  ❌ Exception: {e}")
        
        # Try GET to see what endpoints are available
        print(f"\n🔍 Checking available endpoints...")
        try:
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    content = await response.json()
                    print(f"Root endpoint: {content}")
        except:
            pass
            
        # Try to access docs
        try:
            async with session.get(f"{base_url}/docs") as response:
                if response.status == 200:
                    print("✅ API docs available at /docs")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_stardust_direct())
