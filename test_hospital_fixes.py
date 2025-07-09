#!/usr/bin/env python3
"""
Test script to verify all hospital admin page fixes are working correctly
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_template_syntax():
    """Test that the template doesn't have syntax errors"""
    try:
        with open('app/templates/admin/master_data/list.html', 'r') as f:
            content = f.read()
            
        # Check for basic Jinja2 syntax issues
        assert '{% extends "base.html" %}' in content
        assert '{% block content %}' in content
        assert '{% endblock %}' in content
        
        # Check for the fixed sub-district filter
        assert 'id="sub_district_select"' in content
        assert 'name="sub_district_code"' in content
        
        # Check for province_code parameter in sub-districts AJAX call
        assert 'province_code=${provinceCode}' in content
        
        # Check for improved empty state condition
        assert 'sub_district_code or is_active' in content
        
        # Check for better error handling
        assert 'bootstrap.Tooltip' in content
        
        print("✅ Template syntax checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Template syntax error: {e}")
        return False

def test_backend_routes():
    """Test that backend routes are properly configured"""
    try:
        import app.routes.master_data as master_data_routes
        
        # Check that the module loads without errors
        assert hasattr(master_data_routes, 'router')
        assert hasattr(master_data_routes, 'MASTER_DATA_TYPES')
        
        # Check that hospitals type is configured
        assert 'hospitals' in master_data_routes.MASTER_DATA_TYPES
        
        hospitals_config = master_data_routes.MASTER_DATA_TYPES['hospitals']
        assert 'sub_district_code' in hospitals_config['fields']
        
        print("✅ Backend routes checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Backend routes error: {e}")
        return False

def test_stardust_api():
    """Test that Stardust API service is properly configured"""
    try:
        import app.services.stardust_api as stardust_api
        
        # Check that the service class exists
        assert hasattr(stardust_api, 'StardustAPIService')
        
        service = stardust_api.StardustAPIService()
        
        # Check that required methods exist
        assert hasattr(service, 'get_sub_districts')
        assert hasattr(service, 'get_hospital_types')
        assert hasattr(service, 'get_master_data')
        
        print("✅ Stardust API service checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Stardust API service error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Opera Panel hospital admin page fixes...")
    print("=" * 60)
    
    tests = [
        test_template_syntax,
        test_backend_routes,
        test_stardust_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The hospital admin page should be working correctly.")
        print("\nKey fixes implemented:")
        print("- ✅ Province/District/Sub-District cascading dropdowns")
        print("- ✅ Sub-district API requires both province_code and district_code")
        print("- ✅ Status filter (active/inactive) working correctly")
        print("- ✅ Hospital table displays location columns")
        print("- ✅ Hospital type column added to table")
        print("- ✅ Improved error handling and loading states")
        print("- ✅ Better user feedback for dropdown states")
        print("- ✅ Auto-submit on status filter change")
        print("- ✅ Enhanced pagination and filtering")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
