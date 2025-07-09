#!/usr/bin/env python3
"""
Test raw documents endpoint integration
"""
import requests
import json

def test_raw_documents_integration():
    print("🔍 Testing Raw Documents Endpoint Integration")
    print("=" * 60)
    
    # Login to Opera Panel
    session = requests.Session()
    login_data = {'username': 'admin', 'password': 'Sim!443355'}
    
    try:
        print("1. Logging in...")
        login_response = session.post('http://localhost:5055/auth/login-form', data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        print("✅ Login successful")
        
        # Test raw documents endpoint
        print("\n2. Testing raw documents endpoint...")
        raw_docs_url = 'http://localhost:5055/admin/hospitals-raw-documents'
        print(f"URL: {raw_docs_url}")
        
        raw_docs_response = session.get(f"{raw_docs_url}?limit=1")
        print(f"Status: {raw_docs_response.status_code}")
        
        if raw_docs_response.status_code == 200:
            print("✅ Raw documents endpoint accessible")
            
            try:
                data = raw_docs_response.json()
                print(f"Response type: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    
                    if data.get('success'):
                        print("✅ API response successful")
                        
                        raw_data = data.get('data', {})
                        raw_documents = raw_data.get('raw_documents', [])
                        
                        print(f"📄 Raw documents count: {len(raw_documents)}")
                        
                        if raw_documents:
                            first_doc = raw_documents[0]
                            print(f"📋 Fields in first document: {len(first_doc.keys())}")
                            
                            # Show some key fields
                            key_fields = ['_id', 'name', 'en_name', 'province_code', 'district_code', 'is_active']
                            print("\n📝 Key field values:")
                            for field in key_fields:
                                if field in first_doc:
                                    value = first_doc[field]
                                    print(f"  {field}: {value}")
                            
                            print(f"\n📊 All available fields:")
                            all_fields = list(first_doc.keys())
                            for i, field in enumerate(all_fields[:20]):  # Show first 20
                                print(f"  {i+1:2d}. {field}")
                            if len(all_fields) > 20:
                                print(f"  ... and {len(all_fields) - 20} more")
                        else:
                            print("❌ No raw documents returned")
                    else:
                        print(f"❌ API response not successful: {data.get('message', 'Unknown error')}")
                else:
                    print(f"❌ Unexpected response format: {data}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {raw_docs_response.text[:500]}...")
        else:
            print(f"❌ Raw documents endpoint failed: {raw_docs_response.status_code}")
            print(f"Response: {raw_docs_response.text[:300]}...")
        
        # Test hospital detail page
        print("\n3. Testing hospital detail page integration...")
        hospitals_response = session.get('http://localhost:5055/admin/master-data/hospitals')
        
        if hospitals_response.status_code == 200:
            print("✅ Hospitals page accessible")
            html = hospitals_response.text
            
            # Look for hospital links
            import re
            hospital_links = re.findall(r'/admin/master-data/hospitals/([^"\']+)/edit', html)
            if hospital_links:
                hospital_id = hospital_links[0]
                print(f"📋 Found hospital ID: {hospital_id}")
                
                # Test detail page
                detail_url = f'http://localhost:5055/admin/master-data/hospitals/{hospital_id}'
                detail_response = session.get(detail_url)
                print(f"Detail page status: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    print("✅ Hospital detail page accessible")
                    # Could check for raw document data in template context here
                else:
                    print(f"❌ Hospital detail page failed: {detail_response.status_code}")
            else:
                print("❌ No hospital links found on page")
        else:
            print(f"❌ Hospitals page failed: {hospitals_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_raw_documents_integration()
