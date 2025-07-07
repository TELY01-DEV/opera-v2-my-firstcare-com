#!/usr/bin/env python3
"""
Debug script to test districts loading for sub-districts page
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.stardust_api import StardustAPI

async def test_districts_loading():
    """Test districts loading logic"""
    stardust_api = StardustAPI()
    
    # Use a dummy token for testing
    token = "test_token"
    
    print("Testing districts loading logic...")
    
    # Test 1: Load all districts (no province filter)
    print("\n1. Testing: Load all districts (no province filter)")
    try:
        all_districts = await stardust_api.get_districts(token, 0, 1000)
        print(f"   Result: {len(all_districts.get('data', []))} districts loaded")
        if all_districts.get('data'):
            first_district = all_districts['data'][0]
            print(f"   Sample district: {first_district.get('name', {})}")
    except Exception as e:
        print(f"   Error loading all districts: {e}")
    
    # Test 2: Load districts for a specific province
    print("\n2. Testing: Load districts for province 10 (Bangkok)")
    try:
        filtered_districts = await stardust_api.get_districts(token, 0, 1000, None, 10)
        print(f"   Result: {len(filtered_districts.get('data', []))} districts loaded for province 10")
        if filtered_districts.get('data'):
            first_district = filtered_districts['data'][0]
            print(f"   Sample district: {first_district.get('name', {})}")
    except Exception as e:
        print(f"   Error loading filtered districts: {e}")
    
    # Test 3: Check sub-districts data structure
    print("\n3. Testing: Load sub-districts to check data structure")
    try:
        sub_districts = await stardust_api.get_master_data(token, "sub-districts", 0, 5)
        print(f"   Result: {len(sub_districts.get('data', []))} sub-districts loaded")
        if sub_districts.get('data'):
            first_sub_district = sub_districts['data'][0]
            print(f"   Sample sub-district structure:")
            print(f"     Name: {first_sub_district.get('name', {})}")
            print(f"     Code: {first_sub_district.get('code')}")
            print(f"     Province Code: {first_sub_district.get('province_code')}")
            print(f"     District Code: {first_sub_district.get('district_code')}")
    except Exception as e:
        print(f"   Error loading sub-districts: {e}")

if __name__ == "__main__":
    asyncio.run(test_districts_loading())
