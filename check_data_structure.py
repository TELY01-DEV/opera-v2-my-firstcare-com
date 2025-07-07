#!/usr/bin/env python3
"""
Check the actual data structure returned by Stardust API
"""
import requests
import json

def check_data_structure():
    """Check what the API actually returns"""
    
    # Get authentication token
    login_data = {"username": "operapanel", "password": "Sim!443355"}
    auth_response = requests.post("https://stardust.my-firstcare.com/auth/login", json=login_data)
    
    if auth_response.status_code != 200:
        print("Authentication failed")
        return
    
    auth_data = auth_response.json()
    if "data" in auth_data:
        token = auth_data["data"]["access_token"]
    else:
        token = auth_data["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://stardust.my-firstcare.com"
    
    # Test working endpoints and see their data structure
    working_endpoints = [
        ("Provinces", "/admin/master-data/provinces"),
        ("Districts", "/admin/master-data/districts"),
        ("Sub-Districts", "/admin/master-data/sub_districts"),
        ("Hospital Types", "/admin/master-data/hospital_types"),
        ("Hospitals", "/admin/master-data/hospitals")
    ]
    
    for name, endpoint in working_endpoints:
        print(f"\n=== {name} Data Structure ===")
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, headers=headers, params={"skip": 0, "limit": 1})
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                if "data" in data and len(data["data"]) > 0:
                    first_record = data["data"][0]
                    print(f"First record keys: {list(first_record.keys())}")
                    print(f"First record sample: {json.dumps(first_record, indent=2, ensure_ascii=False)}")
                else:
                    print("No data records found")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    check_data_structure()
