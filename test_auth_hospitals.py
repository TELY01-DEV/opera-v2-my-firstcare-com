#!/usr/bin/env python3
"""
Simple test to login and access the hospitals page
"""
import requests
import json

BASE_URL = "http://localhost:5055"

def test_with_authentication():
    """Test the hospitals page with proper authentication"""
    print("🔐 Testing with Authentication")
    print("=" * 50)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    try:
        # 1. Login first
        login_data = {
            "username": "admin",
            "password": "Sim!443355"
        }
        
        print("1. Logging in...")
        login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Login successful")
            
            # 2. Try to access hospitals page
            print("\n2. Accessing hospitals page...")
            hospitals_response = session.get(f"{BASE_URL}/admin/master-data/hospitals")
            print(f"   Hospitals page status: {hospitals_response.status_code}")
            
            if hospitals_response.status_code == 200:
                print("   ✅ Hospitals page accessible")
                
                # Check for dropdowns in the HTML
                html = hospitals_response.text
                
                if 'id="province_select"' in html:
                    print("   ✅ Province dropdown found")
                    
                    # Check if it has options
                    if '<option value="">' in html and 'provinces' in html:
                        print("   ✅ Province dropdown has options")
                    else:
                        print("   ❌ Province dropdown empty")
                else:
                    print("   ❌ Province dropdown missing")
                    
                if 'id="district_select"' in html:
                    print("   ✅ District dropdown found")
                else:
                    print("   ❌ District dropdown missing")
                    
                if 'id="sub_district_select"' in html:
                    print("   ✅ Sub-district dropdown found")
                else:
                    print("   ❌ Sub-district dropdown missing")
                    
                # Check table columns
                if 'จังหวัด' in html or 'Province' in html:
                    print("   ✅ Province column found in table")
                else:
                    print("   ❌ Province column missing from table")
                    
                # Check for data
                if 'records' in html or 'table' in html:
                    print("   ✅ Table structure found")
                else:
                    print("   ❌ Table structure missing")
                    
            else:
                print(f"   ❌ Cannot access hospitals page (Status: {hospitals_response.status_code})")
                
        else:
            print(f"   ❌ Login failed (Status: {login_response.status_code})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print("\n" + "=" * 50)
    print("Authentication test completed")

if __name__ == "__main__":
    test_with_authentication()
