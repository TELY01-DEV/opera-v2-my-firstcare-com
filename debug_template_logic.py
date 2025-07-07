#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the path so we can import modules
sys.path.append('/Users/kitkamon/VSCode/opera-v2-my-firstcare-com')

from app.services.stardust_api import stardust_api

async def test_template_data():
    """Test what data gets passed to the template"""
    
    # Mock token - we'll just test the data structure
    token = "test_token"
    
    try:
        print("Testing Stardust API data structure...")
        
        # This will fail with auth, but we can see the request structure
        print("The issue is likely in the template logic or data type comparison.")
        print("Let's check the template rendering logic...")
        
        # Create sample data to test the template logic
        sample_districts = [
            {"code": "1001", "name": [{"code": "en", "name": "District 1"}, {"code": "th", "name": "เขต 1"}], "province_code": 10},
            {"code": "1002", "name": [{"code": "en", "name": "District 2"}, {"code": "th", "name": "เขต 2"}], "province_code": "10"},  # String vs int
        ]
        
        sample_provinces = [
            {"code": 10, "name": [{"code": "en", "name": "Province A"}, {"code": "th", "name": "จังหวัด A"}]},
            {"code": "10", "name": [{"code": "en", "name": "Province A"}, {"code": "th", "name": "จังหวัด A"}]},  # Both types
        ]
        
        print("Sample Districts:")
        for district in sample_districts:
            print(f"  District: {district['name']}, Province Code: {district['province_code']} (type: {type(district['province_code'])})")
            
        print("\nSample Provinces:")
        for province in sample_provinces:
            print(f"  Province: {province['name']}, Code: {province['code']} (type: {type(province['code'])})")
            
        print("\nTesting template matching logic:")
        for district in sample_districts:
            matching_province = None
            for province in sample_provinces:
                if str(province['code']) == str(district['province_code']):
                    matching_province = province
                    break
            
            print(f"District {district['code']} -> Province: {matching_province['name'] if matching_province else 'NOT FOUND'}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_template_data())
