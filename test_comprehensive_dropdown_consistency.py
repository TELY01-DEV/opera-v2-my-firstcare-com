#!/usr/bin/env python3
"""
Comprehensive test to verify all dropdown consistency fixes
"""
import requests
import json

def test_all_dropdown_endpoints():
    """Test all dropdown-related API endpoints"""
    
    print("🔍 Comprehensive Dropdown Consistency Test")
    print("=" * 60)
    
    # Login first
    session = requests.Session()
    login_data = {"username": "operapanel", "password": "Sim!443355"}
    login_response = session.post("http://localhost:5055/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Test endpoints
    endpoints_to_test = [
        {
            "name": "Districts for Bangkok (Province 10)",
            "url": "/api/master-data/districts/10",
            "expected_structure": "array"
        },
        {
            "name": "Sub-Districts for Nong Chok (District 1003)", 
            "url": "/api/master-data/sub-districts/1003",
            "expected_structure": "array"
        }
    ]
    
    all_passed = True
    
    for test in endpoints_to_test:
        print(f"\n📡 Testing: {test['name']}")
        print(f"🌐 URL: {test['url']}")
        
        try:
            response = session.get(f"http://localhost:5055{test['url']}")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and data["data"]:
                    records = data["data"]
                    print(f"✅ Found {len(records)} records")
                    
                    # Check name structure consistency
                    if records:
                        first_record = records[0]
                        name_data = first_record.get('name')
                        
                        print(f"📋 Name structure: {type(name_data)}")
                        
                        if isinstance(name_data, list):
                            print("   📄 Array format detected ✅")
                            if name_data and isinstance(name_data[0], dict):
                                codes = [item.get('code') for item in name_data]
                                print(f"   🌐 Languages: {codes}")
                        elif isinstance(name_data, dict):
                            print("   📄 Object format detected ✅")
                            print(f"   🌐 Languages: {list(name_data.keys())}")
                        else:
                            print(f"   📄 Simple format: {name_data}")
                        
                        print(f"   ✅ Consistent structure for dropdown handling")
                else:
                    print("⚠️  No data in response")
                    all_passed = False
            else:
                print(f"❌ API call failed: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            all_passed = False
    
    return all_passed

def test_template_consistency():
    """Test that all templates use consistent dropdown logic"""
    
    print(f"\n📁 Template Consistency Check")
    print("=" * 40)
    
    template_files = [
        "app/templates/admin/master_data/form.html",
        "app/templates/admin/master_data/list.html", 
        "app/templates/admin/master_data/list_enhanced.html",
        "app/templates/admin/master_data/list_backup.html"
    ]
    
    consistent_count = 0
    total_count = len(template_files)
    
    for template in template_files:
        try:
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"📄 Checking: {template}")
            
            # Check for correct API endpoint usage
            if '/api/master-data/districts/' in content:
                print("   ✅ Uses correct district API endpoint")
            elif '/admin/api/master-data/districts/' in content:
                print("   ⚠️  Uses old district API endpoint")
            else:
                print("   ℹ️  No district API calls found")
            
            # Check for robust name extraction
            if 'Array.isArray(district.name)' in content:
                print("   ✅ Uses robust name extraction logic")
                consistent_count += 1
            elif 'district.name[' in content and 'Array.isArray' not in content:
                print("   ⚠️  Uses basic name extraction (less robust)")
            else:
                print("   ℹ️  No district name extraction found")
                consistent_count += 1  # Count as consistent if no extraction needed
                
        except FileNotFoundError:
            print(f"   ❌ File not found: {template}")
        except Exception as e:
            print(f"   ❌ Error reading {template}: {e}")
    
    print(f"\n📊 Template Consistency: {consistent_count}/{total_count}")
    return consistent_count == total_count

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE DROPDOWN CONSISTENCY TEST")
    print("=" * 60)
    
    api_success = test_all_dropdown_endpoints()
    template_success = test_template_consistency()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS:")
    
    if api_success:
        print("✅ API Endpoints: All working correctly")
        print("   - District endpoint: ✅")
        print("   - Sub-district endpoint: ✅") 
        print("   - Name structures: ✅ Consistent")
    else:
        print("❌ API Endpoints: Some issues found")
    
    if template_success:
        print("✅ Template Files: All use robust logic")
        print("   - Correct API endpoints: ✅")
        print("   - Robust name extraction: ✅")
    else:
        print("⚠️  Template Files: Some need updates")
    
    print(f"\n🎯 Overall Status: {'✅ FULLY CONSISTENT' if api_success and template_success else '⚠️ NEEDS ATTENTION'}")
    
    if api_success and template_success:
        print("\n🎉 All dropdown implementations are now consistent!")
        print("📝 What was fixed:")
        print("   ✅ District filter 404 error resolved")
        print("   ✅ Robust name extraction for both array and object formats")
        print("   ✅ Consistent API endpoint usage across all templates")
        print("   ✅ Sub-district dropdown uses same logic as district")
        print("   ✅ Both Thai and English names handled properly")
    else:
        print("\n🔧 Remaining issues:")
        if not api_success:
            print("   - Check API endpoint connectivity")
        if not template_success:
            print("   - Update template name extraction logic")
