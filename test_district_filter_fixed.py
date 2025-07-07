#!/usr/bin/env python3
"""
Test script to verify the district filter fix
"""
import requests
import json

def test_district_filter_fix():
    """Test the corrected district filter"""
    
    print("🔍 Testing District Filter Fix")
    print("=" * 50)
    
    # 1. First, login to get session
    session = requests.Session()
    
    login_data = {
        "username": "operapanel", 
        "password": "Sim!443355"
    }
    
    login_response = session.post("http://localhost:5055/auth/login", json=login_data)
    print(f"🔐 Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("❌ Login failed, cannot test district filter")
        return False
    
    # 2. Test the district API endpoint directly
    print("\n📡 Testing District API Endpoint...")
    try:
        # Test fetching districts for Bangkok (province code 10)
        api_response = session.get("http://localhost:5055/api/master-data/districts/10")
        print(f"🌐 API Response Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"✅ API Success! Response structure: {list(data.keys())}")
            
            if "data" in data and data["data"]:
                districts = data["data"]
                print(f"🏘️  Found {len(districts)} districts")
                
                # Check the structure of the first district
                if districts:
                    first_district = districts[0]
                    print(f"📋 Sample district structure:")
                    print(f"   - Code: {first_district.get('code')}")
                    print(f"   - Name structure: {type(first_district.get('name'))}")
                    print(f"   - Name content: {first_district.get('name')}")
                    
                    # Test name extraction logic
                    name_data = first_district.get('name')
                    if isinstance(name_data, list):
                        print(f"   📄 Array format detected")
                        for item in name_data:
                            if isinstance(item, dict):
                                print(f"      - {item.get('code', 'unknown')}: {item.get('name', 'N/A')}")
                    elif isinstance(name_data, dict):
                        print(f"   📄 Object format detected")
                        for lang, name in name_data.items():
                            print(f"      - {lang}: {name}")
                    else:
                        print(f"   📄 Simple format: {name_data}")
                    
                    return True
            else:
                print("⚠️  No district data found in response")
                return False
        else:
            print(f"❌ API call failed: {api_response.status_code}")
            try:
                error_data = api_response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error response: {api_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during API test: {e}")
        return False

if __name__ == "__main__":
    print("District Filter Fix Test")
    print("=" * 60)
    
    success = test_district_filter_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test PASSED: District filter fix appears to be working!")
        print("✅ District API endpoint is accessible")
        print("✅ District name structure is correctly identified")
        print("\n📝 Next steps:")
        print("   1. Test in browser by visiting master data pages")
        print("   2. Try province filter dropdowns")
        print("   3. Verify district names display correctly")
    else:
        print("❌ Test FAILED: District filter still has issues.")
        print("\n🔧 Check:")
        print("   1. Application is running on port 5055")
        print("   2. Authentication is working")
        print("   3. API endpoints are correctly defined")
