#!/usr/bin/env python3
"""
Comprehensive test for the districts API endpoint fix
"""
import subprocess
import json
import sys

def test_api_endpoint_accessibility():
    """Test if the API endpoint is accessible and returns the right response"""
    
    print("🔍 Districts API Endpoint Fix - Comprehensive Test")
    print("=" * 60)
    
    # Test the endpoint
    endpoint = "http://localhost:5055/api/master-data/districts/11"
    
    try:
        print(f"🌐 Testing endpoint: {endpoint}")
        
        # Use curl to test the endpoint
        result = subprocess.run([
            'curl', '-s', '-i', endpoint
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Curl failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
        
        response = result.stdout
        print(f"📥 Raw Response:\n{response}")
        
        # Parse the response
        lines = response.split('\n')
        status_line = lines[0] if lines else ""
        
        if "HTTP/1.1 404" in status_line:
            print("❌ 404 Not Found - API endpoint is still not accessible")
            return False
        elif "HTTP/1.1 401" in status_line:
            print("✅ 401 Unauthorized - API endpoint exists and requires authentication (EXPECTED)")
            print("🎉 The 404 error has been RESOLVED!")
            return True
        elif "HTTP/1.1 200" in status_line:
            print("✅ 200 OK - API endpoint is working perfectly!")
            return True
        else:
            print(f"❓ Unexpected status: {status_line}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_frontend_fix():
    """Test that the frontend is calling the correct API endpoint"""
    
    print("\n" + "=" * 60)
    print("🔧 Frontend Fix Verification")
    print("=" * 60)
    
    # Check if the frontend files have been updated
    template_file = "/Users/kitkamon/VSCode/opera-v2-my-firstcare-com/app/templates/admin/master_data/list.html"
    
    try:
        with open(template_file, 'r') as f:
            content = f.read()
            
        if "/api/master-data/districts/" in content:
            print("✅ Frontend is calling the correct API endpoint")
            return True
        elif "/api/districts?province_code=" in content:
            print("❌ Frontend is still calling the old API endpoint")
            return False
        else:
            print("❓ Could not find API calls in frontend")
            return False
            
    except Exception as e:
        print(f"❌ Error reading template file: {str(e)}")
        return False

def test_route_configuration():
    """Test that the route configuration is correct"""
    
    print("\n" + "=" * 60)
    print("🛠️  Route Configuration Verification")
    print("=" * 60)
    
    main_file = "/Users/kitkamon/VSCode/opera-v2-my-firstcare-com/main.py"
    
    try:
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if master_data router is included twice (with and without prefix)
        router_includes = content.count("app.include_router(master_data.router")
        
        if router_includes >= 2:
            print("✅ Master data router is included multiple times for different prefixes")
            return True
        else:
            print(f"❌ Master data router only included {router_includes} time(s)")
            return False
            
    except Exception as e:
        print(f"❌ Error reading main.py: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Districts API 404 Error - Resolution Test Suite")
    print("=" * 60)
    
    tests = [
        ("API Endpoint Accessibility", test_api_endpoint_accessibility),
        ("Frontend Fix", test_frontend_fix),
        ("Route Configuration", test_route_configuration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The 404 error for /api/districts has been RESOLVED!")
        print("✅ The frontend now calls the correct API endpoint")
        print("✅ The backend routing is configured correctly")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
