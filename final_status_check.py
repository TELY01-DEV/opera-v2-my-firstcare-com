#!/usr/bin/env python3
"""
Final status check for all user issues
"""
import requests
import re
from urllib.parse import urlencode

BASE_URL = "http://localhost:5055"

def final_status_check():
    """Final comprehensive check of all user issues"""
    print("🎯 FINAL STATUS CHECK - User Issues")
    print("=" * 60)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    try:
        # Login
        login_data = {
            "username": "admin",
            "password": "Sim!443355"
        }
        
        print("1. Authentication...")
        login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed (Status: {login_response.status_code})")
            return
        
        print("   ✅ Login successful")
        
        # Issue 1: Dropdowns should list all statuses
        print("\n2. 🔍 ISSUE 1: Province, district, sub-district filters list ALL status")
        
        base_response = session.get(f"{BASE_URL}/admin/master-data/hospitals")
        base_html = base_response.text
        
        # Count dropdown options
        province_options = len(re.findall(r'<option value="[^"]*"[^>]*>[^<]+</option>', re.search(r'<select[^>]*name="province_code"[^>]*>(.*?)</select>', base_html, re.DOTALL).group(1) if re.search(r'<select[^>]*name="province_code"[^>]*>(.*?)</select>', base_html, re.DOTALL) else ""))
        
        print(f"   ✅ Province dropdown: {province_options} options")
        
        # Test cascading
        province_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?province_code=10")
        province_html = province_response.text
        district_options = len(re.findall(r'<option value="[^"]*"[^>]*>[^<]+</option>', re.search(r'<select[^>]*name="district_code"[^>]*>(.*?)</select>', province_html, re.DOTALL).group(1) if re.search(r'<select[^>]*name="district_code"[^>]*>(.*?)</select>', province_html, re.DOTALL) else ""))
        
        print(f"   ✅ District dropdown (with province): {district_options} options")
        
        # Test sub-district
        district_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?province_code=10&district_code=1003")
        district_html = district_response.text
        sub_district_options = len(re.findall(r'<option value="[^"]*"[^>]*>[^<]+</option>', re.search(r'<select[^>]*name="sub_district_code"[^>]*>(.*?)</select>', district_html, re.DOTALL).group(1) if re.search(r'<select[^>]*name="sub_district_code"[^>]*>(.*?)</select>', district_html, re.DOTALL) else ""))
        
        print(f"   ✅ Sub-district dropdown (with province+district): {sub_district_options} options")
        
        # Issue 2: Table sub-district data
        print("\n3. 🔍 ISSUE 2: Table sub-district data population")
        
        table_rows = re.findall(r'<tr[^>]*class="slide-in"[^>]*>(.*?)</tr>', base_html, re.DOTALL)
        sub_district_populated = 0
        sub_district_empty = 0
        
        for row in table_rows[:10]:  # Check first 10 rows
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 5:  # Sub-district column
                sub_district_cell = re.sub(r'<[^>]+>', '', cells[4]).strip()
                if sub_district_cell and sub_district_cell != '-':
                    sub_district_populated += 1
                else:
                    sub_district_empty += 1
        
        print(f"   Sub-district data: {sub_district_populated} populated, {sub_district_empty} empty")
        if sub_district_populated > 0:
            print("   ✅ Sub-district data is being populated")
        else:
            print("   ❌ Sub-district data shows empty ('-') for all rows")
        
        # Issue 3: Status filtering
        print("\n4. 🔍 ISSUE 3: Status filter active/inactive")
        
        all_response = session.get(f"{BASE_URL}/admin/master-data/hospitals")
        all_html = all_response.text
        all_rows = len(re.findall(r'<tr[^>]*class="slide-in"[^>]*>', all_html))
        
        active_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?is_active=true")
        active_html = active_response.text
        active_rows = len(re.findall(r'<tr[^>]*class="slide-in"[^>]*>', active_html))
        
        inactive_response = session.get(f"{BASE_URL}/admin/master-data/hospitals?is_active=false")
        inactive_html = inactive_response.text
        inactive_rows = len(re.findall(r'<tr[^>]*class="slide-in"[^>]*>', inactive_html))
        
        print(f"   All hospitals: {all_rows} rows")
        print(f"   Active filter: {active_rows} rows")
        print(f"   Inactive filter: {inactive_rows} rows")
        
        if active_rows != all_rows or inactive_rows != all_rows:
            print("   ✅ Status filtering is working (different row counts)")
        else:
            print("   ❌ Status filtering may not be working (same row counts)")
        
        # Count actual status badges in active filter
        active_badges = len(re.findall(r'<span class="badge bg-success"[^>]*>.*?Active|ใช้งาน.*?</span>', active_html, re.DOTALL))
        inactive_badges = len(re.findall(r'<span class="badge bg-danger"[^>]*>.*?Inactive|ไม่ใช้งาน.*?</span>', active_html, re.DOTALL))
        print(f"   Active filter results: {active_badges} active badges, {inactive_badges} inactive badges")
        
        # Issue 4: Hospital type column
        print("\n5. 🔍 ISSUE 4: Hospital type column shows correct single type")
        
        max_types_per_row = 0
        for i, row in enumerate(table_rows[:5]):
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 6:  # Hospital type column
                type_cell = cells[5]
                type_spans = len(re.findall(r'<span[^>]*class="text-success"[^>]*>[^<]+</span>', type_cell))
                max_types_per_row = max(max_types_per_row, type_spans)
        
        print(f"   Maximum hospital types per row: {max_types_per_row}")
        if max_types_per_row <= 1:
            print("   ✅ Hospital type logic working (max 1 type per row)")
        else:
            print(f"   ❌ Hospital type logic broken (max {max_types_per_row} types per row)")
        
        # Issue 5: JavaScript cascading
        print("\n6. 🔍 ISSUE 5: JavaScript cascading functionality")
        
        js_elements = [
            ('province_select', 'Province dropdown ID'),
            ('district_select', 'District dropdown ID'),
            ('sub_district_select', 'Sub-district dropdown ID'),
            ('addEventListener', 'Event listeners'),
            ('fetch(`/api/master-data/districts/', 'Districts API fetch'),
            ('fetch(`/api/master-data/sub-districts/', 'Sub-districts API fetch'),
        ]
        
        js_working = 0
        js_total = len(js_elements)
        
        for element, description in js_elements:
            if element in base_html:
                print(f"   ✅ {description}: Found")
                js_working += 1
            else:
                print(f"   ❌ {description}: Missing")
        
        print(f"   JavaScript functionality: {js_working}/{js_total} working")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 FINAL SUMMARY")
        print("=" * 60)
        
        issues_fixed = 0
        total_issues = 5
        
        if province_options >= 6 and district_options >= 10 and sub_district_options >= 5:
            print("✅ ISSUE 1: Province, district, sub-district filters - WORKING")
            issues_fixed += 1
        else:
            print("❌ ISSUE 1: Province, district, sub-district filters - NEEDS WORK")
        
        if sub_district_populated > 0:
            print("✅ ISSUE 2: Table sub-district data population - WORKING")
            issues_fixed += 1
        else:
            print("❌ ISSUE 2: Table sub-district data population - NEEDS WORK")
        
        if active_rows != all_rows or inactive_rows != all_rows:
            print("✅ ISSUE 3: Status filter active/inactive - WORKING")
            issues_fixed += 1
        else:
            print("❌ ISSUE 3: Status filter active/inactive - NEEDS WORK")
        
        if max_types_per_row <= 1:
            print("✅ ISSUE 4: Hospital type column - FIXED")
            issues_fixed += 1
        else:
            print("❌ ISSUE 4: Hospital type column - BROKEN")
        
        if js_working >= 4:
            print("✅ ISSUE 5: JavaScript cascading - MOSTLY WORKING")
            issues_fixed += 1
        else:
            print("❌ ISSUE 5: JavaScript cascading - NEEDS WORK")
        
        print(f"\n🎯 OVERALL STATUS: {issues_fixed}/{total_issues} issues resolved")
        
        if issues_fixed == total_issues:
            print("🎉 ALL ISSUES RESOLVED!")
        else:
            print(f"⚠️  {total_issues - issues_fixed} issues still need attention")
        
        print(f"\n🔗 Test the page: {BASE_URL}/admin/master-data/hospitals")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_status_check()
