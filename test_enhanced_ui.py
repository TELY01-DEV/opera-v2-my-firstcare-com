#!/usr/bin/env python3
"""
Visual verification test for enhanced UI deployment
"""
import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "http://localhost:5055"
LOGIN_URL = f"{BASE_URL}/auth/login"
HOSPITALS_URL = f"{BASE_URL}/admin/master-data/hospitals"

# Test credentials
TEST_USERNAME = "operapanel"
TEST_PASSWORD = "Sim!443355"

async def login_and_get_session():
    """Login and get session cookies"""
    connector = aiohttp.TCPConnector(ssl=False)
    session = aiohttp.ClientSession(connector=connector)
    
    try:
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        async with session.post(LOGIN_URL, json=login_data) as response:
            if response.status == 200:
                print("✅ Login successful")
                return session
            else:
                print(f"❌ Login failed with status {response.status}")
                await session.close()
                return None
                
    except Exception as e:
        print(f"❌ Login error: {e}")
        await session.close()
        return None

async def verify_enhanced_ui(session: aiohttp.ClientSession):
    """Verify that enhanced UI elements are present"""
    try:
        async with session.get(HOSPITALS_URL) as response:
            if response.status == 200:
                html_content = await response.text()
                
                # Check for enhanced CSS
                enhanced_css_loaded = "/static/enhanced-styles.css" in html_content
                print(f"✅ Enhanced CSS loaded: {enhanced_css_loaded}")
                
                # Check for enhanced class names
                enhanced_classes = [
                    "fade-in",
                    "slide-in", 
                    "search-filter-bar",
                    "status-filter-container",
                    "enhanced-table"
                ]
                
                found_classes = []
                for cls in enhanced_classes:
                    if cls in html_content:
                        found_classes.append(cls)
                
                print(f"✅ Enhanced classes found: {len(found_classes)}/{len(enhanced_classes)}")
                print(f"   Found: {', '.join(found_classes)}")
                
                # Check for improved structure
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Check for page pretitle (enhanced element)
                pretitle = soup.find(class_="page-pretitle")
                print(f"✅ Page pretitle found: {pretitle is not None}")
                
                # Check for enhanced buttons
                enhanced_buttons = soup.find_all("a", class_=re.compile(r"btn.*btn-primary"))
                print(f"✅ Enhanced buttons found: {len(enhanced_buttons)}")
                
                # Check for filter enhancements
                filter_section = soup.find(class_="search-filter-bar") or soup.find(class_="filter-section")
                print(f"✅ Enhanced filter section found: {filter_section is not None}")
                
                # Check for status indicators
                status_badges = soup.find_all(class_=re.compile(r"badge.*status"))
                print(f"✅ Status badges found: {len(status_badges)}")
                
                return {
                    "enhanced_css": enhanced_css_loaded,
                    "enhanced_classes": len(found_classes),
                    "page_pretitle": pretitle is not None,
                    "enhanced_buttons": len(enhanced_buttons),
                    "filter_section": filter_section is not None,
                    "status_badges": len(status_badges)
                }
                
            else:
                print(f"❌ Failed to load page: {response.status}")
                return None
                
    except Exception as e:
        print(f"❌ UI verification error: {e}")
        return None

async def main():
    """Main verification function"""
    print("🎨 Verifying Enhanced UI Deployment...")
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    session = await login_and_get_session()
    if not session:
        return
    
    try:
        # Step 2: Verify enhanced UI elements
        print("\n2️⃣ Verifying enhanced UI elements...")
        ui_result = await verify_enhanced_ui(session)
        
        if ui_result:
            print("\n📊 UI Enhancement Summary:")
            print(f"   Enhanced CSS: {'✅' if ui_result['enhanced_css'] else '❌'}")
            print(f"   Enhanced Classes: {ui_result['enhanced_classes']}/5")
            print(f"   Page Pretitle: {'✅' if ui_result['page_pretitle'] else '❌'}")
            print(f"   Enhanced Buttons: {ui_result['enhanced_buttons']}")
            print(f"   Filter Section: {'✅' if ui_result['filter_section'] else '❌'}")
            print(f"   Status Badges: {ui_result['status_badges']}")
            
            # Overall assessment
            score = (
                ui_result['enhanced_css'] +
                (ui_result['enhanced_classes'] >= 3) +
                ui_result['page_pretitle'] +
                (ui_result['enhanced_buttons'] > 0) +
                ui_result['filter_section']
            )
            
            if score >= 4:
                print("\n✅ Enhanced UI successfully deployed! 🎉")
            elif score >= 2:
                print("\n⚠️ Enhanced UI partially deployed")
            else:
                print("\n❌ Enhanced UI deployment may have issues")
                
        else:
            print("\n❌ Failed to verify UI enhancements")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
