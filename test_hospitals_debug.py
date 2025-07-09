#!/usr/bin/env python3
"""
Debug script to test the hospitals page functionality
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:5055"
HOSPITALS_URL = f"{BASE_URL}/admin/master-data/hospitals"

async def test_hospitals_page():
    """Test the hospitals page with different filters"""
    print("🔍 Testing Hospitals Page Functionality")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Test basic page load
            print("\n1. Testing basic page load...")
            async with session.get(HOSPITALS_URL) as response:
                if response.status == 200:
                    text = await response.text()
                    print(f"✅ Page loaded successfully (Status: {response.status})")
                    
                    # Check if dropdowns are present
                    if 'id="province_select"' in text:
                        print("✅ Province dropdown found")
                    else:
                        print("❌ Province dropdown missing")
                        
                    if 'id="district_select"' in text:
                        print("✅ District dropdown found")
                    else:
                        print("❌ District dropdown missing")
                        
                    if 'id="sub_district_select"' in text:
                        print("✅ Sub-district dropdown found")
                    else:
                        print("❌ Sub-district dropdown missing")
                        
                    # Check for table headers
                    if 'จังหวัด' in text or 'Province' in text:
                        print("✅ Province column found in table")
                    else:
                        print("❌ Province column missing from table")
                        
                    if 'อำเภอ' in text or 'District' in text:
                        print("✅ District column found in table")
                    else:
                        print("❌ District column missing from table")
                        
                    if 'ตำบล' in text or 'Sub-District' in text:
                        print("✅ Sub-district column found in table")
                    else:
                        print("❌ Sub-district column missing from table")
                        
                    if 'ประเภท' in text or 'Type' in text:
                        print("✅ Hospital type column found in table")
                    else:
                        print("❌ Hospital type column missing from table")
                        
                else:
                    print(f"❌ Failed to load page (Status: {response.status})")
                    
        except Exception as e:
            print(f"❌ Error testing hospitals page: {e}")
            
        # 2. Test API endpoints
        print("\n2. Testing API endpoints...")
        try:
            # Test provinces API
            provinces_url = f"{BASE_URL}/api/master-data/provinces"
            async with session.get(provinces_url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Provinces API working (Status: {response.status})")
                    print(f"   Data structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Provinces API failed (Status: {response.status})")
                    
            # Test districts API
            districts_url = f"{BASE_URL}/api/master-data/districts/1"
            async with session.get(districts_url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Districts API working (Status: {response.status})")
                    print(f"   Data structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Districts API failed (Status: {response.status})")
                    
            # Test sub-districts API
            sub_districts_url = f"{BASE_URL}/api/master-data/sub-districts/1?province_code=1"
            async with session.get(sub_districts_url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Sub-districts API working (Status: {response.status})")
                    print(f"   Data structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                else:
                    print(f"❌ Sub-districts API failed (Status: {response.status})")
                    
        except Exception as e:
            print(f"❌ Error testing API endpoints: {e}")
            
        # 3. Test with different filters
        print("\n3. Testing filters...")
        try:
            # Test with province filter
            params = {"province_code": "1"}
            async with session.get(HOSPITALS_URL, params=params) as response:
                if response.status == 200:
                    print(f"✅ Province filter working (Status: {response.status})")
                else:
                    print(f"❌ Province filter failed (Status: {response.status})")
                    
            # Test with status filter
            params = {"is_active": "true"}
            async with session.get(HOSPITALS_URL, params=params) as response:
                if response.status == 200:
                    print(f"✅ Status filter working (Status: {response.status})")
                else:
                    print(f"❌ Status filter failed (Status: {response.status})")
                    
        except Exception as e:
            print(f"❌ Error testing filters: {e}")
            
    print("\n" + "=" * 60)
    print("Debug test completed")

if __name__ == "__main__":
    asyncio.run(test_hospitals_page())
