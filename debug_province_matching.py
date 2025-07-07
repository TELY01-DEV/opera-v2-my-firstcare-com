#!/usr/bin/env python3

import asyncio
import httpx
import json

async def debug_province_matching():
    """Debug the province matching issue in districts list"""
    
    # Get authentication token
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            "http://localhost:5055/auth/login",
            json={"username": "operapanel", "password": "Sim!443355"}
        )
        
        if login_response.status_code != 200:
            print("Login failed")
            return
            
        # Extract token from cookie
        session_cookie = None
        for cookie in login_response.cookies:
            if cookie.name == "session":
                session_cookie = cookie.value
                break
        
        if not session_cookie:
            print("No session cookie found")
            return
            
        print(f"Session cookie: {session_cookie[:50]}...")
        
        # Get districts data
        districts_response = await client.get(
            "http://localhost:5055/admin/master-data/districts",
            cookies={"session": session_cookie},
            follow_redirects=True
        )
        
        print(f"Districts response status: {districts_response.status_code}")
        
        # Try to get actual API data directly
        # First, let me check what's in the session cookie to get the token
        import base64
        from urllib.parse import unquote
        
        try:
            # Decode the session cookie to get the token
            decoded_cookie = unquote(session_cookie)
            print(f"Decoded cookie: {decoded_cookie[:100]}...")
            
            # The cookie should contain the access_token
            if "access_token" in decoded_cookie:
                # Extract the JWT token from the cookie
                import re
                token_match = re.search(r'"access_token":\s*"([^"]+)"', decoded_cookie)
                if token_match:
                    jwt_token = token_match.group(1)
                    print(f"JWT Token: {jwt_token[:50]}...")
                    
                    # Now test the actual Stardust API calls
                    headers = {"Authorization": f"Bearer {jwt_token}"}
                    
                    # Get provinces
                    provinces_response = await client.get(
                        "https://stardust.my-firstcare.com/admin/master-data/provinces?skip=0&limit=10",
                        headers=headers
                    )
                    print(f"Provinces API status: {provinces_response.status_code}")
                    
                    if provinces_response.status_code == 200:
                        provinces_data = provinces_response.json()
                        print("Sample provinces:")
                        for province in provinces_data.get("data", [])[:3]:
                            print(f"  Province Code: {province.get('code')} (type: {type(province.get('code'))})")
                            print(f"  Province Name: {province.get('name')}")
                    
                    # Get districts
                    districts_response = await client.get(
                        "https://stardust.my-firstcare.com/admin/master-data/districts?skip=0&limit=10&sort=updated_at&order=desc",
                        headers=headers
                    )
                    print(f"Districts API status: {districts_response.status_code}")
                    
                    if districts_response.status_code == 200:
                        districts_data = districts_response.json()
                        print("Sample districts:")
                        for district in districts_data.get("data", [])[:3]:
                            print(f"  District Code: {district.get('code')} (type: {type(district.get('code'))})")
                            print(f"  District Name: {district.get('name')}")
                            print(f"  Province Code: {district.get('province_code')} (type: {type(district.get('province_code'))})")
                            
        except Exception as e:
            print(f"Error parsing cookie: {e}")

if __name__ == "__main__":
    asyncio.run(debug_province_matching())
