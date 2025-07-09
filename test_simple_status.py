#!/usr/bin/env python3
"""
Simple test for status filter
"""
import requests
import json

def test_status_filter():
    session = requests.Session()
    
    # Login
    login_data = {"username": "admin", "password": "Sim!443355"}
    login_response = session.post("http://localhost:5055/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Test different status filters
    filters = [
        ("No filter", ""),
        ("Active", "?status=active"),
        ("Inactive", "?status=inactive"),
        ("Status 1", "?status=1"),
        ("Status 0", "?status=0"),
    ]
    
    for filter_name, filter_param in filters:
        url = f"http://localhost:5055/admin/master-data/hospitals{filter_param}"
        print(f"\n🔍 Testing {filter_name}: {url}")
        
        response = session.get(url)
        if response.status_code == 200:
            # Count rows in table
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    print(f"   Rows: {len(rows)}")
                    
                    # Check first few rows' status
                    for i, row in enumerate(rows[:3]):
                        cells = row.find_all('td')
                        if len(cells) >= 7:  # Status should be in the 7th column
                            status_text = cells[6].text.strip()
                            print(f"   Row {i+1} status: {status_text}")
                        if i >= 2:  # Only check first 3 rows
                            break
                else:
                    print("   No tbody found")
            else:
                print("   No table found")
        else:
            print(f"   Failed: {response.status_code}")

if __name__ == "__main__":
    test_status_filter()
