#!/usr/bin/env python3
"""
Test current state of hospitals admin page
"""
import requests
import sys
from bs4 import BeautifulSoup

def test_hospitals_page():
    print("🔍 Testing current state of hospitals admin page...")
    
    # Login
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'Sim!443355'}
    
    try:
        login_response = session.post('http://localhost:5055/auth/login-form', data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        print("✅ Login successful")
        
        # Get hospitals page
        hospitals_response = session.get('http://localhost:5055/admin/master-data/hospitals')
        
        if hospitals_response.status_code != 200:
            print(f"❌ Failed to get hospitals page: {hospitals_response.status_code}")
            return False
            
        print("✅ Hospitals page loaded")
        
        # Parse HTML
        soup = BeautifulSoup(hospitals_response.text, 'html.parser')
        
        # Check status filter
        print("\n🔍 Testing status filter:")
        
        # Test all hospitals (no filter)
        all_response = session.get('http://localhost:5055/admin/master-data/hospitals')
        all_soup = BeautifulSoup(all_response.text, 'html.parser')
        all_table = all_soup.find('table')
        all_rows = all_table.find('tbody').find_all('tr') if all_table and all_table.find('tbody') else []
        print(f"  All hospitals: {len(all_rows)} rows")
        
        # Test active hospitals
        active_response = session.get('http://localhost:5055/admin/master-data/hospitals?status=active')
        active_soup = BeautifulSoup(active_response.text, 'html.parser')
        active_table = active_soup.find('table')
        active_rows = active_table.find('tbody').find_all('tr') if active_table and active_table.find('tbody') else []
        print(f"  Active hospitals: {len(active_rows)} rows")
        
        # Test inactive hospitals
        inactive_response = session.get('http://localhost:5055/admin/master-data/hospitals?status=inactive')
        inactive_soup = BeautifulSoup(inactive_response.text, 'html.parser')
        inactive_table = inactive_soup.find('table')
        inactive_rows = inactive_table.find('tbody').find_all('tr') if inactive_table and inactive_table.find('tbody') else []
        print(f"  Inactive hospitals: {len(inactive_rows)} rows")
        
        # Check if filtering is working
        if len(all_rows) > 0:
            if len(active_rows) == len(all_rows) and len(inactive_rows) == len(all_rows):
                print("❌ Status filter not working - all queries return same number of rows")
            else:
                print("✅ Status filter appears to be working")
        
        # Check table structure
        print("\n🔍 Testing table structure:")
        table = soup.find('table')
        if table:
            headers = table.find('thead')
            if headers:
                header_cells = headers.find_all('th')
                print(f"  Headers: {[h.text.strip() for h in header_cells]}")
                
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"  Data rows: {len(rows)}")
                
                if rows:
                    # Check first row
                    first_row = rows[0]
                    cells = first_row.find_all('td')
                    print(f"  First row data: {[c.text.strip() for c in cells]}")
                    
                    # Check for sub-district data
                    if len(cells) >= 4:  # Assuming sub-district is 4th column
                        sub_district_cell = cells[3].text.strip()
                        if sub_district_cell == "-":
                            print("❌ Sub-district data showing '-'")
                        else:
                            print(f"✅ Sub-district data: {sub_district_cell}")
                    
                    # Check for hospital type data
                    if len(cells) >= 5:  # Assuming hospital type is 5th column
                        hospital_type_cell = cells[4].text.strip()
                        if hospital_type_cell == "-":
                            print("❌ Hospital type data showing '-'")
                        else:
                            print(f"✅ Hospital type data: {hospital_type_cell}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_hospitals_page()
