#!/usr/bin/env python3
"""
Test script to examine the actual HTML content of the hospitals page
"""
import requests
import re

BASE_URL = "http://localhost:5055"

def test_html_content():
    """Test HTML content of hospitals page"""
    print("🔍 Examining HTML Content of Hospitals Page")
    print("=" * 60)
    
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
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed (Status: {login_response.status_code})")
            return
        
        print("   ✅ Login successful")
        
        # 2. Get hospitals page
        print("\n2. Fetching hospitals page...")
        hospitals_response = session.get(f"{BASE_URL}/admin/master-data/hospitals")
        
        if hospitals_response.status_code != 200:
            print(f"   ❌ Cannot access hospitals page (Status: {hospitals_response.status_code})")
            return
        
        html = hospitals_response.text
        print("   ✅ Hospitals page fetched successfully")
        
        # 3. Extract table headers
        print("\n3. Analyzing table headers...")
        
        # Look for table headers
        th_pattern = r'<th[^>]*>(.*?)</th>'
        th_matches = re.findall(th_pattern, html, re.DOTALL)
        
        if th_matches:
            print("   Found table headers:")
            for i, header in enumerate(th_matches):
                clean_header = re.sub(r'<[^>]+>', '', header).strip()
                print(f"     {i+1}. {clean_header}")
        else:
            print("   ❌ No table headers found")
        
        # 4. Check for specific text patterns
        print("\n4. Checking for specific text patterns...")
        
        text_checks = [
            ('จังหวัด', 'Province (Thai)'),
            ('Province', 'Province (English)'),
            ('อำเภอ', 'District (Thai)'),
            ('District', 'District (English)'),
            ('ตำบล', 'Sub-District (Thai)'),
            ('Sub-District', 'Sub-District (English)'),
            ('ประเภท', 'Type (Thai)'),
            ('Type', 'Type (English)'),
            ('hospital_type_found', 'Hospital type logic'),
            ('data_type', 'Data type variable'),
            ('hospitals', 'Hospitals data type')
        ]
        
        for text, description in text_checks:
            if text in html:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Missing")
        
        # 5. Check data_type specific sections
        print("\n5. Checking data_type conditions...")
        
        # Look for hospitals-specific table headers
        hospitals_pattern = r'{% if data_type == \'hospitals\' %}.*?<th[^>]*>(.*?)</th>.*?{% endif %}'
        hospitals_matches = re.findall(hospitals_pattern, html, re.DOTALL)
        
        if hospitals_matches:
            print("   Found hospitals-specific headers:")
            for header in hospitals_matches:
                clean_header = re.sub(r'<[^>]+>', '', header).strip()
                print(f"     - {clean_header}")
        
        # 6. Extract table rows sample
        print("\n6. Analyzing table rows...")
        
        # Look for table rows
        tr_pattern = r'<tr[^>]*class="slide-in"[^>]*>(.*?)</tr>'
        tr_matches = re.findall(tr_pattern, html, re.DOTALL)
        
        if tr_matches:
            print(f"   Found {len(tr_matches)} table rows")
            if len(tr_matches) > 0:
                print("   First row analysis:")
                # Count cells in first row
                td_pattern = r'<td[^>]*>(.*?)</td>'
                td_matches = re.findall(td_pattern, tr_matches[0], re.DOTALL)
                print(f"     - Number of cells: {len(td_matches)}")
                
                # Show first few cell contents
                for i, cell in enumerate(td_matches[:5]):
                    clean_cell = re.sub(r'<[^>]+>', '', cell).strip()
                    if clean_cell:
                        print(f"     - Cell {i+1}: {clean_cell[:50]}...")
        else:
            print("   ❌ No table rows found")
        
        # 7. Check for JavaScript functions
        print("\n7. Checking JavaScript functionality...")
        
        js_checks = [
            ('loadDistricts', 'Load districts function'),
            ('loadSubDistricts', 'Load sub-districts function'),
            ('onchange', 'Auto-submit functionality'),
            ('province_select', 'Province dropdown ID'),
            ('district_select', 'District dropdown ID'),
            ('sub_district_select', 'Sub-district dropdown ID')
        ]
        
        for js_element, description in js_checks:
            if js_element in html:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Missing")
        
        print("\n" + "=" * 60)
        print("✅ HTML Content Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_content()
