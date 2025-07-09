#!/usr/bin/env python3
"""
Test script to verify raw document data is displayed on hospital detail page.
"""
import requests
import json
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "http://localhost:5055"
USERNAME = "admin"
PASSWORD = "admin"

def test_hospital_detail_with_raw_data():
    """Test that hospital detail page shows raw document data"""
    
    # Step 1: Login
    print("Step 1: Logging in...")
    session = requests.Session()
    
    # Get login page first
    login_page = session.get(f"{BASE_URL}/login")
    if login_page.status_code != 200:
        print(f"❌ Failed to access login page: {login_page.status_code}")
        return False
    
    # Extract any CSRF token if needed
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
    
    # Login data
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    # Perform login
    login_response = session.post(f"{BASE_URL}/auth/login-form", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Check if redirected to dashboard (successful login)
    if '/admin/dashboard' not in login_response.url and '/admin/login' in login_response.url:
        print("❌ Login failed - still on login page")
        return False
    
    print("✅ Login successful")
    
    # Step 2: Get hospitals list to find a hospital ID
    print("\nStep 2: Getting hospitals list...")
    hospitals_response = session.get(f"{BASE_URL}/admin/master-data/hospitals")
    if hospitals_response.status_code != 200:
        print(f"❌ Failed to get hospitals list: {hospitals_response.status_code}")
        return False
    
    # Parse hospitals page to find a hospital ID
    soup = BeautifulSoup(hospitals_response.text, 'html.parser')
    hospital_links = soup.find_all('a', href=lambda x: x and '/admin/master-data/hospitals/' in x and '/edit' not in x and x.count('/') == 4)
    
    if not hospital_links:
        print("❌ No hospital detail links found")
        return False
    
    # Extract hospital ID from the first link
    hospital_link = hospital_links[0]['href']
    hospital_id = hospital_link.split('/')[-1]
    print(f"✅ Found hospital ID: {hospital_id}")
    
    # Step 3: Test hospital detail page
    print(f"\nStep 3: Testing hospital detail page...")
    detail_url = f"{BASE_URL}/admin/master-data/hospitals/{hospital_id}"
    detail_response = session.get(detail_url)
    
    if detail_response.status_code != 200:
        print(f"❌ Failed to get hospital detail: {detail_response.status_code}")
        return False
    
    # Parse the detail page HTML
    soup = BeautifulSoup(detail_response.text, 'html.parser')
    
    # Check for raw document data section
    raw_data_section = soup.find('div', string=lambda text: text and 'Raw MongoDB Document' in text)
    raw_data_title = soup.find('div', class_='datagrid-title', string=lambda text: text and ('Raw MongoDB Document' in text or 'ข้อมูล MongoDB ดิบ' in text))
    
    if raw_data_section or raw_data_title:
        print("✅ Raw MongoDB Document section found!")
        
        # Look for the details/summary element
        details_element = soup.find('details')
        if details_element:
            summary = details_element.find('summary')
            if summary and ('Raw MongoDB Document' in summary.get_text() or 'ข้อมูล MongoDB ดิบ' in summary.get_text()):
                print("✅ Raw document data expandable section found!")
                
                # Look for pre element with raw data
                pre_element = details_element.find('pre')
                if pre_element:
                    print("✅ Raw data pre element found!")
                    raw_data_text = pre_element.get_text()
                    if raw_data_text and len(raw_data_text) > 10:
                        print(f"✅ Raw data content found (length: {len(raw_data_text)} chars)")
                        print(f"Raw data preview: {raw_data_text[:200]}...")
                        return True
                    else:
                        print("❌ Raw data content is empty or too short")
                else:
                    print("❌ No pre element found in raw data section")
            else:
                print("❌ Summary element doesn't contain raw data text")
        else:
            print("❌ No details element found for raw data")
    else:
        print("❌ Raw MongoDB Document section not found")
        
        # Debug: Show what sections are available
        print("\nDebug: Available sections in detail page:")
        card_titles = soup.find_all('h3', class_='card-title')
        for title in card_titles:
            print(f"- {title.get_text().strip()}")
        
        datagrid_titles = soup.find_all('div', class_='datagrid-title')
        for title in datagrid_titles:
            print(f"- {title.get_text().strip()}")
    
    return False

if __name__ == "__main__":
    print("Testing hospital detail page with raw document data...")
    success = test_hospital_detail_with_raw_data()
    if success:
        print("\n🎉 Test passed! Raw document data is displayed on hospital detail page.")
    else:
        print("\n❌ Test failed! Raw document data is not displayed properly.")
