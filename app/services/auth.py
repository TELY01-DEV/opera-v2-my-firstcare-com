"""
Authentication service for Opera Panel
Handles JWT authentication with Stardust-V1 API
"""
import httpx
import os
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.models.auth import User, Token, LoginRequest, UserProfile, SystemAccess

# Environment variables
STARDUST_AUTH_URL = os.getenv("STARDUST_AUTH_URL", "https://stardust.my-firstcare.com")
SECRET_KEY = os.getenv("SECRET_KEY", "opera-panel-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.auth_url = STARDUST_AUTH_URL
        self.client = httpx.AsyncClient()

    async def login(self, login_data: LoginRequest) -> Token:
        """Login user with Stardust-V1 API"""
        try:
            response = await self.client.post(
                f"{self.auth_url}/auth/login",
                json={
                    "username": login_data.username,
                    "password": login_data.password
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle the new API response structure
                if "access_token" in data:
                    # Direct response format
                    return Token(
                        access_token=data["access_token"],
                        token_type=data.get("token_type", "bearer"),
                        expires_in=data.get("expires_in")
                    )
                else:
                    # Wrapped response format
                    token_data = data.get("data", data)
                    return Token(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "bearer"),
                        expires_in=token_data.get("expires_in")
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Authentication service unavailable: {str(e)}"
            )

    async def get_user_profile(self, token: str) -> UserProfile:
        """Get user profile from Stardust-V1 API"""
        try:
            print(f"DEBUG: Making request to {self.auth_url}/auth/me with token: {token[:20]}...")
            response = await self.client.get(
                f"{self.auth_url}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"DEBUG: Stardust API response status: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                print(f"DEBUG: Raw API response: {response_data}")
                
                # Handle the new API response structure with data wrapper
                if "data" in response_data:
                    data = response_data["data"]
                    print(f"DEBUG: Using wrapped data: {data.get('username', 'unknown')}")
                else:
                    data = response_data
                    print(f"DEBUG: Using direct data: {data.get('username', 'unknown')}")
                
                # Create SystemAccess object if system_access data exists
                system_access = None
                if "system_access" in data:
                    system_access = SystemAccess(**data["system_access"])
                
                return UserProfile(
                    id=data.get("id"),
                    username=data["username"],
                    email=data.get("email"),
                    full_name=data.get("full_name"),
                    role=data["role"],
                    profile_photo=data.get("profile_photo"),
                    phone=data.get("phone"),
                    permissions=data.get("permissions", []),
                    authentication_source=data.get("authentication_source"),
                    token_type=data.get("token_type"),
                    system_access=system_access
                )
            else:
                print(f"DEBUG: Stardust API error response: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        except httpx.RequestError as e:
            print(f"DEBUG: Network error connecting to Stardust: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Authentication service unavailable: {str(e)}"
            )

    def verify_token(self, token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Get user profile from Stardust-V1
    profile = await auth_service.get_user_profile(token)
    
    return User(
        id=profile.id or profile.username,  # Use username as fallback ID
        username=profile.username,
        email=profile.email,
        full_name=profile.full_name,
        role=profile.role,
        profile_photo=profile.profile_photo,
        phone=profile.phone,
        permissions=profile.permissions or [],
        system_access=profile.system_access
    )

async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current user from session (for template rendering)"""
    try:
        token = request.session.get("access_token")
        if not token:
            return None
        
        profile = await auth_service.get_user_profile(token)
        return User(
            id=profile.id or profile.username,  # Use username as fallback ID
            username=profile.username,
            email=profile.email,
            full_name=profile.full_name,
            role=profile.role,
            profile_photo=profile.profile_photo,
            phone=profile.phone,
            permissions=profile.permissions or [],
            system_access=profile.system_access
        )
    except:
        return None
