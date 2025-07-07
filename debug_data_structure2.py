#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/kitkamon/VSCode/opera-v2-my-firstcare-com')

import asyncio
import json
from app.services.stardust_api import stardust_api

async def check_data_structure():
    """Check the actual data structure from Stardust API"""
    
    api = stardust_api
    
    try:
        # Get token
        token_response = await api.login("operapanel", "opera2024")
        token = token_response.get("access_token")
        
        if not token:
            print("Failed to get token")
            return
            
        print(f"Got token: {token[:50]}...")
        
        # Test provinces endpoint
        print("\n=== Testing Provinces ===")
        provinces_response = await api.get_provinces(token, 0, 5)
        print(f"Response keys: {list(provinces_response.keys())}")
        
        provinces = provinces_response.get("data", [])
        if provinces:
            print(f"Total provinces: {len(provinces)}")
            print(f"First province structure:")
            first_province = provinces[0]
            print(json.dumps(first_province, indent=2, ensure_ascii=False))
            
            # Check name field specifically
            if "name" in first_province:
                name_field = first_province["name"]
                print(f"Name field type: {type(name_field)}")
                print(f"Name field value: {name_field}")
        
        # Test districts endpoint
        print("\n=== Testing Districts ===")
        districts_response = await api.get_districts(token, 0, 5)
        print(f"Response keys: {list(districts_response.keys())}")
        
        districts = districts_response.get("data", [])
        if districts:
            print(f"Total districts: {len(districts)}")
            print(f"First district structure:")
            first_district = districts[0]
            print(json.dumps(first_district, indent=2, ensure_ascii=False))
            
        # Test sub-districts endpoint
        print("\n=== Testing Sub-Districts ===")
        sub_districts_response = await api.get_sub_districts(token, 0, 5)
        print(f"Response keys: {list(sub_districts_response.keys())}")
        
        sub_districts = sub_districts_response.get("data", [])
        if sub_districts:
            print(f"Total sub-districts: {len(sub_districts)}")
            print(f"First sub-district structure:")
            first_sub_district = sub_districts[0]
            print(json.dumps(first_sub_district, indent=2, ensure_ascii=False))
            
        # Test hospital types endpoint
        print("\n=== Testing Hospital Types ===")
        hospital_types_response = await api.get_hospital_types(token, 0, 5)
        print(f"Response keys: {list(hospital_types_response.keys())}")
        
        hospital_types = hospital_types_response.get("data", [])
        if hospital_types:
            print(f"Total hospital types: {len(hospital_types)}")
            print(f"First hospital type structure:")
            first_hospital_type = hospital_types[0]
            print(json.dumps(first_hospital_type, indent=2, ensure_ascii=False))
            
        # Test hospitals endpoint  
        print("\n=== Testing Hospitals ===")
        hospitals_response = await api.get_hospitals(token, 0, 5)
        print(f"Response keys: {list(hospitals_response.keys())}")
        
        hospitals = hospitals_response.get("data", [])
        if hospitals:
            print(f"Total hospitals: {len(hospitals)}")
            print(f"First hospital structure:")
            first_hospital = hospitals[0]
            print(json.dumps(first_hospital, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_data_structure())
