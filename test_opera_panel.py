#!/usr/bin/env python3
"""
Test Opera Panel API endpoints directly
"""
import asyncio
import aiohttp
import json
import sys

OPERA_PANEL_URL = "http://localhost:5055"

async def test_opera_panel():
    """Test Opera Panel endpoints"""
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Opera Panel connectivity...")
        
        # First check if Opera Panel is accessible
        try:
            async with session.get(f"{OPERA_PANEL_URL}/health") as response:
                if response.status == 200:
                    print("✅ Opera Panel is healthy")
                else:
                    print(f"❌ Opera Panel health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to Opera Panel: {e}")
            return
        
        # Try to login and get a session
        print("\n🔐 Trying to authenticate...")
        try:
            login_data = {
                "username": "operapanel",
                "password": "Sim!443355"
            }
            
            async with session.post(f"{OPERA_PANEL_URL}/auth/login", json=login_data) as response:
                print(f"Login response status: {response.status}")
                if response.status == 200:
                    print("✅ Login successful")
                    
                    # Try to access master data page
                    print("\n📊 Testing master data access...")
                    async with session.get(f"{OPERA_PANEL_URL}/admin/master-data/provinces") as data_response:
                        print(f"Provinces page status: {data_response.status}")
                        if data_response.status == 200:
                            print("✅ Successfully accessed provinces page")
                            content = await data_response.text()
                            if "error" in content.lower():
                                print("⚠️  Page contains errors")
                                # Find specific error messages
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if 'error' in line.lower() or 'exception' in line.lower():
                                        print(f"Error line {i}: {line.strip()}")
                            else:
                                print("✅ Page loaded without visible errors")
                        else:
                            print(f"❌ Failed to access provinces page: {data_response.status}")
                            error_text = await data_response.text()
                            print(f"Error: {error_text[:200]}...")
                else:
                    print(f"❌ Login failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    asyncio.run(test_opera_panel())
