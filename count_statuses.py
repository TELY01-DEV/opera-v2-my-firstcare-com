#!/usr/bin/env python3
"""
Count active vs inactive hospitals
"""
import requests
import sys
from bs4 import BeautifulSoup

def count_statuses():
    print("🔍 Counting active vs inactive hospitals...")
    
    # Login
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'Sim!443355'}
    
    try:
        login_response = session.post('http://localhost:5055/auth/login-form', data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        print("✅ Login successful")
        
        # Get all hospitals
        url = "http://localhost:5055/admin/master-data/hospitals"
        response = session.get(url)
        
        if response.status_code != 200:
            print(f"❌ Failed to get page: {response.status_code}")
            return False
        
        # Parse and count statuses
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            print("❌ No table found")
            return False
        
        tbody = table.find('tbody')
        if not tbody:
            print("❌ No table body found")
            return False
        
        rows = tbody.find_all('tr')
        print(f"📊 Found {len(rows)} total rows")
        
        active_count = 0
        inactive_count = 0
        
        for i, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 7:  # Status should be in column 7
                status_cell = cells[6].text.strip()
                
                if status_cell.lower() == 'active':
                    active_count += 1
                elif status_cell.lower() == 'inactive':
                    inactive_count += 1
                else:
                    print(f"Row {i+1}: Unknown status '{status_cell}'")
        
        print(f"📊 Status counts:")
        print(f"  ✅ Active: {active_count}")
        print(f"  ❌ Inactive: {inactive_count}")
        print(f"  📊 Total: {active_count + inactive_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    count_statuses()
