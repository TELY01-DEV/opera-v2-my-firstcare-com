#!/usr/bin/env python3
"""
Final comprehensive test of all user issues
"""
import requests
from bs4 import BeautifulSoup

def run_comprehensive_test():
    print("🎯 COMPREHENSIVE TEST - Hospital Admin Page")
    print("=" * 60)
    
    # Login
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'Sim!443355'}
    login_response = session.post('http://localhost:5055/auth/login-form', data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    print("✅ Login successful")
    
    # Get base page
    base_response = session.get('http://localhost:5055/admin/master-data/hospitals')
    if base_response.status_code != 200:
        print(f"❌ Base page failed: {base_response.status_code}")
        return False
        
    print("✅ Base page accessible")
    
    # Parse page
    soup = BeautifulSoup(base_response.text, 'html.parser')
    
    # Test 1: Check dropdowns
    print("\n🔍 ISSUE 1: Dropdown filters")
    has_province = 'id="province_select"' in base_response.text
    has_district = 'id="district_select"' in base_response.text  
    has_subdistrict = 'id="sub_district_select"' in base_response.text
    
    print(f"   Province dropdown: {'✅' if has_province else '❌'}")
    print(f"   District dropdown: {'✅' if has_district else '❌'}")
    print(f"   Sub-district dropdown: {'✅' if has_subdistrict else '❌'}")
    
    # Test 2: Check table columns
    print("\n🔍 ISSUE 2: Table structure")
    table = soup.find('table')
    if table:
        headers = table.find('thead')
        if headers:
            header_texts = [th.text.strip() for th in headers.find_all('th')]
            print(f"   Table headers: {header_texts}")
            
            has_province_col = any('Province' in h or 'จังหวัด' in h for h in header_texts)
            has_district_col = any('District' in h or 'อำเภอ' in h for h in header_texts)
            has_subdistrict_col = any('Sub-District' in h or 'ตำบล' in h for h in header_texts)
            has_type_col = any('Type' in h or 'ประเภท' in h for h in header_texts)
            has_status_col = any('Status' in h or 'สถานะ' in h for h in header_texts)
            
            print(f"   Province column: {'✅' if has_province_col else '❌'}")
            print(f"   District column: {'✅' if has_district_col else '❌'}")
            print(f"   Sub-district column: {'✅' if has_subdistrict_col else '❌'}")
            print(f"   Type column: {'✅' if has_type_col else '❌'}")
            print(f"   Status column: {'✅' if has_status_col else '❌'}")
    
    # Test 3: Status filtering
    print("\n🔍 ISSUE 3: Status filtering")
    
    # Test all hospitals
    all_response = session.get('http://localhost:5055/admin/master-data/hospitals')
    all_soup = BeautifulSoup(all_response.text, 'html.parser')
    all_table = all_soup.find('table')
    all_rows = all_table.find('tbody').find_all('tr') if all_table and all_table.find('tbody') else []
    
    # Test active hospitals  
    active_response = session.get('http://localhost:5055/admin/master-data/hospitals?status=active')
    active_soup = BeautifulSoup(active_response.text, 'html.parser')
    active_table = active_soup.find('table')
    active_rows = active_table.find('tbody').find_all('tr') if active_table and active_table.find('tbody') else []
    
    # Test inactive hospitals
    inactive_response = session.get('http://localhost:5055/admin/master-data/hospitals?status=inactive')
    inactive_soup = BeautifulSoup(inactive_response.text, 'html.parser')
    inactive_table = inactive_soup.find('table')
    inactive_rows = inactive_table.find('tbody').find_all('tr') if inactive_table and inactive_table.find('tbody') else []
    
    print(f"   All hospitals: {len(all_rows)} rows")
    print(f"   Active hospitals: {len(active_rows)} rows")
    print(f"   Inactive hospitals: {len(inactive_rows)} rows")
    
    # Validate status filtering
    if len(active_rows) > 0 and len(active_rows) < len(all_rows):
        print("   ✅ Active filter working")
    else:
        print("   ❌ Active filter not working properly")
        
    if len(inactive_rows) > 0 and len(inactive_rows) < len(all_rows):
        print("   ✅ Inactive filter working")
    else:
        print("   ❌ Inactive filter not working properly")
    
    # Test 4: Hospital type column
    print("\n🔍 ISSUE 4: Hospital type column")
    if all_rows:
        first_row = all_rows[0]
        cells = first_row.find_all('td')
        if len(cells) >= 6:  # Assuming type is around 6th column
            type_cell = cells[5].text.strip()
            if type_cell and type_cell != '-':
                print(f"   ✅ Hospital type showing: {type_cell}")
            else:
                print("   ❌ Hospital type column empty or showing '-'")
        else:
            print("   ❌ Not enough table columns")
    
    # Test 5: Sub-district data
    print("\n🔍 ISSUE 5: Sub-district data")
    if all_rows:
        first_row = all_rows[0]
        cells = first_row.find_all('td')
        if len(cells) >= 5:  # Assuming sub-district is around 5th column
            subdistrict_cell = cells[4].text.strip()
            if subdistrict_cell and subdistrict_cell != '-':
                print(f"   ✅ Sub-district data showing: {subdistrict_cell}")
            else:
                print("   ❌ Sub-district column empty or showing '-'")
        else:
            print("   ❌ Not enough table columns")
    
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST COMPLETED")
    
    return True

if __name__ == "__main__":
    run_comprehensive_test()
