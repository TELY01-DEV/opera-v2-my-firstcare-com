"""
Authentication models for Opera Panel
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import os

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None

class SystemAccess(BaseModel):
    can_access_admin: bool = False
    can_modify_data: bool = False
    can_view_data: bool = False
    is_superadmin: bool = False

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str  # superadmin, operator, viewer
    is_active: bool = True
    profile_photo: Optional[str] = None
    phone: Optional[str] = None
    permissions: Optional[List[str]] = []
    system_access: Optional[SystemAccess] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @field_validator('profile_photo')
    @classmethod
    def validate_profile_photo(cls, v):
        if not v:
            return '/static/avatar-default.svg'
        
        # If it's already a full URL, return as is
        if v.startswith('http'):
            return v
        
        # If it's a relative path starting with /static, prepend the OLD Stardust server URL for assets
        if v.startswith('/static'):
            # Profile photos are still hosted on the old server
            return f"https://stardust-v1.my-firstcare.com{v}"
        
        return '/static/avatar-default.svg'

class UserProfile(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str
    profile_photo: Optional[str] = None
    phone: Optional[str] = None
    permissions: Optional[List[str]] = []
    authentication_source: Optional[str] = None
    token_type: Optional[str] = None
    system_access: Optional[SystemAccess] = None
    
    @field_validator('profile_photo')
    @classmethod
    def validate_profile_photo(cls, v):
        if not v:
            return '/static/avatar-default.png'
        
        # If it's already a full URL, return as is
        if v.startswith('http'):
            return v
        
        # If it's a relative path starting with /static, prepend the OLD Stardust server URL for assets
        if v.startswith('/static'):
            # Profile photos are still hosted on the old server
            return f"https://stardust-v1.my-firstcare.com{v}"
        
        return '/static/avatar-default.svg'
