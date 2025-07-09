#!/usr/bin/env python3
"""
Test status filter specifically
"""
import requests
import sys
from bs4 import BeautifulSoup

def test_status_filter():
    print("🔍 Testing status filter in detail...")
    
    # Login
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'Sim!443355'}
    
    try:
        login_response = session.post('http://localhost:5055/auth/login-form', data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        print("✅ Login successful")
        
        # Test different status values
        test_cases = [
            ("all", ""),
            ("active", "active"),
            ("inactive", "inactive"),
            ("true", "true"),
            ("false", "false"),
            ("1", "1"),
            ("0", "0"),
        ]
        
        for test_name, status_value in test_cases:
            print(f"\n🔍 Testing status: {test_name} (value: '{status_value}')")
            
            # Build URL with status parameter
            if status_value:
                url = f"http://localhost:5055/admin/master-data/hospitals?status={status_value}"
            else:
                url = "http://localhost:5055/admin/master-data/hospitals"
            
            print(f"  URL: {url}")
            
            # Get response
            response = session.get(url)
            
            if response.status_code != 200:
                print(f"  ❌ Failed to get page: {response.status_code}")
                continue
                
            # Parse and count rows
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    print(f"  📊 Found {len(rows)} rows")
                    
                    # Check first few rows for status
                    for i, row in enumerate(rows[:3]):
                        cells = row.find_all('td')
                        if len(cells) >= 7:  # Status should be in column 7
                            status_cell = cells[6].text.strip()
                            print(f"    Row {i+1} status: '{status_cell}'")
                        else:
                            print(f"    Row {i+1}: Not enough cells ({len(cells)})")
                else:
                    print("  ❌ No table body found")
            else:
                print("  ❌ No table found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_status_filter()
