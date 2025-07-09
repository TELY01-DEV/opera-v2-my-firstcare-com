#!/usr/bin/env python3
"""
Test script to specifically verify the user's reported issues
"""
import requests
from urllib.parse import urlencode, parse_qs, urlparse
import re

BASE_URL = "http://localhost:5055"

def test_specific_issues():
    """Test the specific issues reported by the user"""
    print("🔍 Testing Specific User Issues")
    print("=" * 60)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    try:
        # Login
        login_data = {
            "username": "admin",
            "password": "Sim!443355"
        }
        
        print("1. Logging in...")
        login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed (Status: {login_response.status_code})")
            return
        
        print("   ✅ Login successful")
        
        # Issue 1: Province, district, sub-district filters should list ALL status
        print("\n2. 🔍 ISSUE 1: Province, district, sub-district filters list ALL status")
        
        # Test base page to see what's loaded
        base_response = session.get(f"{BASE_URL}/admin/master-data/hospitals")
        base_html = base_response.text
        
        # Extract province options from the HTML
        province_pattern = r'<select[^>]*name="province_code"[^>]*>(.*?)</select>'
        province_match = re.search(province_pattern, base_html, re.DOTALL)
        
        if province_match:
            options = re.findall(r'<option value="([^"]*)"[^>]*>([^<]+)</option>', province_match.group(1))
            print(f"   ✅ Province dropdown: {len(options)} options found")
            if len(options) <= 3:  # Show first few options
                for value, text in options:
                    print(f"       - {value}: {text.strip()}")
        else:
            print("   ❌ Province dropdown not found")
        
        # Test district dropdown after selecting a province
        province_test_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?province_code=10")
        province_html = province_test_response.text
        
        district_pattern = r'<select[^>]*name="district_code"[^>]*>(.*?)</select>'
        district_match = re.search(district_pattern, province_html, re.DOTALL)
        
        if district_match:
            options = re.findall(r'<option value="([^"]*)"[^>]*>([^<]+)</option>', district_match.group(1))
            print(f"   ✅ District dropdown (province=10): {len(options)} options found")
            if len(options) <= 3:
                for value, text in options:
                    print(f"       - {value}: {text.strip()}")
        else:
            print("   ❌ District dropdown not found")
        
        # Test sub-district dropdown
        district_test_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?province_code=10&district_code=1003")
        district_html = district_test_response.text
        
        sub_district_pattern = r'<select[^>]*name="sub_district_code"[^>]*>(.*?)</select>'
        sub_district_match = re.search(sub_district_pattern, district_html, re.DOTALL)
        
        if sub_district_match:
            options = re.findall(r'<option value="([^"]*)"[^>]*>([^<]+)</option>', sub_district_match.group(1))
            print(f"   ✅ Sub-district dropdown (province=10, district=1003): {len(options)} options found")
            if len(options) <= 3:
                for value, text in options:
                    print(f"       - {value}: {text.strip()}")
        else:
            print("   ❌ Sub-district dropdown not found")
        
        # Issue 2: Table not populate sub-district data
        print("\n3. 🔍 ISSUE 2: Table sub-district data population")
        
        # Count rows with sub-district data
        table_row_pattern = r'<tr[^>]*class="slide-in"[^>]*>(.*?)</tr>'
        table_rows = re.findall(table_row_pattern, base_html, re.DOTALL)
        
        print(f"   Found {len(table_rows)} table rows")
        
        if table_rows:
            # Analyze first few rows for sub-district data
            for i, row in enumerate(table_rows[:3]):
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 5:  # Sub-district should be around 5th column
                    sub_district_cell = cells[4]  # 5th column (0-indexed)
                    clean_cell = re.sub(r'<[^>]+>', '', sub_district_cell).strip()
                    print(f"   Row {i+1} sub-district: {clean_cell[:30]}...")
        
        # Issue 3: Status filter not working
        print("\n4. 🔍 ISSUE 3: Status filter active/inactive")
        
        # Test active filter
        active_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?is_active=true")
        active_html = active_response.text
        
        active_rows = re.findall(table_row_pattern, active_html, re.DOTALL)
        print(f"   Active filter: {len(active_rows)} rows")
        
        # Test inactive filter
        inactive_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?is_active=false")
        inactive_html = inactive_response.text
        
        inactive_rows = re.findall(table_row_pattern, inactive_html, re.DOTALL)
        print(f"   Inactive filter: {len(inactive_rows)} rows")
        
        # Test all hospitals (no filter)
        all_rows = re.findall(table_row_pattern, base_html, re.DOTALL)
        print(f"   All hospitals (no filter): {len(all_rows)} rows")
        
        # Verify filtering is working
        if len(active_rows) != len(all_rows) or len(inactive_rows) != len(all_rows):
            print("   ✅ Status filtering is working (different row counts)")
        else:
            print("   ❌ Status filtering may not be working (same row counts)")
        
        # Check status badges in active filter
        if active_rows:
            active_badges = re.findall(r'<span class="badge bg-success"[^>]*>.*?ใช้งาน|Active.*?</span>', active_html, re.DOTALL)
            inactive_badges = re.findall(r'<span class="badge bg-danger"[^>]*>.*?ไม่ใช้งาน|Inactive.*?</span>', active_html, re.DOTALL)
            print(f"   Active filter: {len(active_badges)} active badges, {len(inactive_badges)} inactive badges")
        
        # Issue 4: Hospital type column shows all types
        print("\n5. 🔍 ISSUE 4: Hospital type column shows all types")
        
        # Check hospital type column in first few rows
        if table_rows:
            for i, row in enumerate(table_rows[:3]):
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 6:  # Hospital type should be around 6th column
                    type_cell = cells[5]  # 6th column (0-indexed)
                    clean_cell = re.sub(r'<[^>]+>', '', type_cell).strip()
                    print(f"   Row {i+1} hospital type: {clean_cell[:50]}...")
        
        # Check if hospital_type_found logic is in the template source (check for single types per row)
        # Count hospital types per row to see if there are multiple types
        hospital_type_counts = []
        if table_rows:
            for i, row in enumerate(table_rows[:5]):
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 6:  # Hospital type should be around 6th column
                    type_cell = cells[5]  # 6th column (0-indexed)
                    # Count how many hospital type spans are in this cell
                    type_spans = re.findall(r'<span[^>]*class="text-success"[^>]*>([^<]+)</span>', type_cell)
                    hospital_type_counts.append(len(type_spans))
                    print(f"   Row {i+1}: {len(type_spans)} hospital type(s) - {[span.strip() for span in type_spans]}")
        
        if hospital_type_counts:
            max_types = max(hospital_type_counts)
            if max_types <= 1:
                print("   ✅ Hospital type prevention logic working (max 1 type per row)")
            else:
                print(f"   ❌ Hospital type prevention logic not working (max {max_types} types per row)")
        else:
            print("   ❌ Hospital type data not found")
        
        # Issue 5: Check JavaScript functions
        print("\n6. 🔍 JavaScript Functions")
        
        js_functions = [
            ('loadDistricts', 'Districts loading function'),
            ('loadSubDistricts', 'Sub-districts loading function'),
            ('province_select', 'Province select ID'),
            ('district_select', 'District select ID'),
            ('sub_district_select', 'Sub-district select ID'),
            ('addEventListener', 'Event listeners'),
            ('fetch(`/api/master-data/districts/', 'Districts API fetch'),
            ('fetch(`/api/master-data/sub-districts/', 'Sub-districts API fetch'),
        ]
        
        for func_name, description in js_functions:
            if func_name in base_html:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Missing")
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY OF ISSUES")
        print("=" * 60)
        
        print("\n📊 Based on the analysis above:")
        print("1. Check if province/district/sub-district dropdowns have sufficient options")
        print("2. Verify sub-district data is populated in table rows")
        print("3. Confirm status filtering returns different row counts")
        print("4. Ensure hospital type column shows single type per row")
        print("5. Verify JavaScript functions for cascading dropdowns")
        
        print("\n🔗 Visit the page to test manually:")
        print(f"   {BASE_URL}/admin/master-data/hospitals")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_issues()
