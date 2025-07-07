#!/usr/bin/env python3
"""
Development authentication bypass script
Temporarily modify the Opera Panel to allow direct access for testing templates
"""

# Create a simple patch script
patch_content = '''
import os
from fastapi import Request
from app.models.auth import User

# Mock user for development
def mock_get_current_user(request: Request):
    """Mock authentication for development"""
    return User(
        id="test-user-id",
        username="dev-user", 
        email="dev@test.com",
        role="admin",
        full_name="Development User"
    )

# Override the auth check
async def _mock_check_auth(request: Request):
    """Mock auth check that always succeeds"""
    user = mock_get_current_user(request)
    token = "mock-token-for-development"
    return user, token
'''

print("📝 Creating development authentication patch...")
print("This will temporarily bypass authentication for template testing.")

with open("/Users/kitkamon/VSCode/opera-v2-my-firstcare-com/dev_auth_patch.py", "w") as f:
    f.write(patch_content)

print("✅ Patch file created.")
print("To apply this patch, modify master_data.py to use the mock functions.")
print("⚠️  Remember to remove this in production!")
