#!/usr/bin/env python3
"""
Test Stardust API endpoints directly to debug the provinces issue
"""
import requests
import json

def test_stardust_endpoints():
    """Test Stardust API endpoints directly"""
    
    # Get authentication token
    print("🔐 Getting authentication token...")
    login_data = {"username": "operapanel", "password": "Sim!443355"}
    
    auth_response = requests.post("https://stardust.my-firstcare.com/auth/login", json=login_data)
    print(f"Auth status: {auth_response.status_code}")
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.text}")
        return
    
    auth_data = auth_response.json()
    if "data" in auth_data:
        token = auth_data["data"]["access_token"]
    else:
        token = auth_data["access_token"]
    
    print(f"✅ Got token: {token[:20]}...")
    
    # Test each master data endpoint
    base_url = "https://stardust.my-firstcare.com"
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("Provinces", "/admin/master-data/province"),
        ("Districts", "/admin/master-data/district"),
        ("Sub-Districts", "/admin/master-data/sub_district"),
        ("Hospital Types", "/admin/master-data/hospital_type"),
        ("Hospitals/Organizations", "/admin/master-data/organization")
    ]
    
    print("\n🧪 Testing Stardust API endpoints...")
    
    for name, endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, headers=headers, params={"skip": 0, "limit": 5})
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"{status_icon} {name}: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   Error: {response.text[:200]}")
            else:
                data = response.json()
                if "data" in data:
                    count = len(data["data"]) if isinstance(data["data"], list) else "N/A"
                    print(f"   Records: {count}")
                else:
                    print(f"   Response: {str(data)[:100]}")
                    
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    # Test all possible endpoint variations
    print("\n🔍 Testing all possible endpoint variations...")
    
    all_endpoints = [
        ("Provinces", "/admin/master-data/provinces"),
        ("Districts", "/admin/master-data/districts"),
        ("Sub-Districts", "/admin/master-data/sub-districts"),
        ("Sub-Districts Alt", "/admin/master-data/sub_districts"),
        ("Hospital Types", "/admin/master-data/hospital-types"),
        ("Hospital Types Alt", "/admin/master-data/hospital_types"),
        ("Hospitals", "/admin/master-data/hospitals"),
        ("Organizations", "/admin/master-data/organizations"),
        ("Organization", "/admin/master-data/organization"),
    ]
    
    working_endpoints = []
    
    for name, endpoint in all_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, headers=headers, params={"skip": 0, "limit": 1})
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"{status_icon} {name}: {response.status_code} - {endpoint}")
            
            if response.status_code == 200:
                working_endpoints.append((name, endpoint))
                data = response.json()
                if "data" in data:
                    count = len(data["data"]) if isinstance(data["data"], list) else "N/A"
                    print(f"   Records found: {count}")
                    
        except Exception as e:
            print(f"❌ {name}: Exception - {e}")
    
    print(f"\n✅ Working endpoints found: {len(working_endpoints)}")
    for name, endpoint in working_endpoints:
        print(f"   • {name}: {endpoint}")
    
    print("\n🌐 Testing Opera Panel endpoints...")
    
    # Test our local endpoints  
    session = requests.Session()
    login_response = session.post("http://localhost:5055/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        local_endpoints = [
            ("Provinces Page", "/admin/master-data/provinces"),
            ("Districts Page", "/admin/master-data/districts"),
            ("Sub-Districts Page", "/admin/master-data/sub-districts"),
            ("Hospital Types Page", "/admin/master-data/hospital-types"),
            ("Hospitals Page", "/admin/master-data/hospitals")
        ]
        
        for name, endpoint in local_endpoints:
            try:
                url = f"http://localhost:5055{endpoint}"
                response = session.get(url)
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                print(f"{status_icon} {name}: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"   Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ {name}: Exception - {e}")

if __name__ == "__main__":
    test_stardust_endpoints()
