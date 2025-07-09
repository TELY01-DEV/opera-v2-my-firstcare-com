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
                        refresh_token=data.get("refresh_token"),
                        expires_in=data.get("expires_in")
                    )
                else:
                    # Wrapped response format
                    token_data = data.get("data", data)
                    return Token(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "bearer"),
                        refresh_token=token_data.get("refresh_token"),
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

    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        try:
            response = await self.client.post(
                f"{self.auth_url}/auth/refresh",
                json={"refresh_token": refresh_token},
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
                        refresh_token=data.get("refresh_token", refresh_token),  # Keep existing refresh token if not provided
                        expires_in=data.get("expires_in")
                    )
                else:
                    # Wrapped response format
                    token_data = data.get("data", data)
                    return Token(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "bearer"),
                        refresh_token=token_data.get("refresh_token", refresh_token),  # Keep existing refresh token if not provided
                        expires_in=token_data.get("expires_in")
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Authentication service unavailable: {str(e)}"
            )

    async def get_user_profile(self, token: str) -> UserProfile:
        """Get user profile from Stardust-V1 API"""
        try:
            response = await self.client.get(
                f"{self.auth_url}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Handle the new API response structure with data wrapper
                if "data" in response_data:
                    data = response_data["data"]
                else:
                    data = response_data
                
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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
        except httpx.RequestError as e:
            print(f"Network error connecting to Stardust: {str(e)}")
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

async def get_current_user_with_refresh(request: Request) -> Optional[User]:
    """Get current user from session with automatic token refresh"""
    try:
        token = request.session.get("access_token")
        refresh_token = request.session.get("refresh_token")
        
        if not token:
            return None
        
        # Try to get user profile with current token
        try:
            profile = await auth_service.get_user_profile(token)
            return User(
                id=profile.id or profile.username,
                username=profile.username,
                email=profile.email,
                full_name=profile.full_name,
                role=profile.role,
                profile_photo=profile.profile_photo,
                phone=profile.phone,
                permissions=profile.permissions or [],
                system_access=profile.system_access
            )
        except HTTPException as e:
            # If token is invalid/expired and we have refresh token, try to refresh
            if e.status_code == 401 and refresh_token:
                print(f"DEBUG: Access token expired, attempting refresh...")
                try:
                    new_token = await auth_service.refresh_token(refresh_token)
                    # Update session with new tokens
                    request.session["access_token"] = new_token.access_token
                    if new_token.refresh_token:
                        request.session["refresh_token"] = new_token.refresh_token
                    
                    # Try again with new token
                    profile = await auth_service.get_user_profile(new_token.access_token)
                    return User(
                        id=profile.id or profile.username,
                        username=profile.username,
                        email=profile.email,
                        full_name=profile.full_name,
                        role=profile.role,
                        profile_photo=profile.profile_photo,
                        phone=profile.phone,
                        permissions=profile.permissions or [],
                        system_access=profile.system_access
                    )
                except HTTPException as refresh_error:
                    print(f"Token refresh failed: {refresh_error.detail}")
                    return None
            return None
    except Exception as e:
        print(f"Error in get_current_user_with_refresh: {str(e)}")
        return None

async def get_valid_token(request: Request) -> Optional[str]:
    """Get a valid access token, refreshing if necessary"""
    try:
        token = request.session.get("access_token")
        refresh_token = request.session.get("refresh_token")
        
        if not token:
            return None
        
        # Try to use the current token by making a simple API call
        try:
            await auth_service.get_user_profile(token)
            return token  # Token is valid
        except HTTPException as e:
            # If token is invalid/expired and we have refresh token, try to refresh
            if e.status_code == 401 and refresh_token:
                try:
                    new_token = await auth_service.refresh_token(refresh_token)
                    # Update session with new tokens
                    request.session["access_token"] = new_token.access_token
                    if new_token.refresh_token:
                        request.session["refresh_token"] = new_token.refresh_token
                    return new_token.access_token
                except HTTPException as refresh_error:
                    print(f"Token refresh failed: {refresh_error.detail}")
                    return None
            return None
    except Exception as e:
        print(f"Error in get_valid_token: {str(e)}")
        return None
