"""
Master Data models for Opera Panel
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class MasterDataBase(BaseModel):
    """Base model for master data"""
    name: Optional[Dict[str, str]] = None  # Multi-language support
    code: Optional[str] = None
    is_active: bool = True
    province_code: Optional[int] = None
    district_code: Optional[int] = None
    sub_district_code: Optional[int] = None
    additional_fields: Optional[Dict[str, Any]] = None


class MasterDataCreate(MasterDataBase):
    """Model for creating master data"""
    data_type: str


class MasterDataUpdate(BaseModel):
    """Model for updating master data"""
    name: Optional[Dict[str, str]] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    province_code: Optional[int] = None
    district_code: Optional[int] = None
    sub_district_code: Optional[int] = None
    additional_fields: Optional[Dict[str, Any]] = None


class MasterDataResponse(MasterDataBase):
    """Model for master data response"""
    id: str
    data_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Province(BaseModel):
    """Province model"""
    id: str
    name: Dict[str, str]  # {"en": "Bangkok", "th": "กรุงเทพฯ"}
    code: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class District(BaseModel):
    """District model"""
    id: str
    name: Dict[str, str]
    code: str
    province_code: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SubDistrict(BaseModel):
    """Sub-District model"""
    id: str
    name: Dict[str, str]
    code: str
    district_code: int
    province_code: int
    postal_code: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HospitalType(BaseModel):
    """Hospital Type model"""
    id: str
    name: Dict[str, str]
    code: str
    description: Optional[Dict[str, str]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Hospital(BaseModel):
    """Hospital model"""
    id: str
    name: Dict[str, str]
    code: str
    hospital_type_code: Optional[str] = None
    address: Optional[str] = None
    province_code: Optional[int] = None
    district_code: Optional[int] = None
    sub_district_code: Optional[int] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MasterDataListResponse(BaseModel):
    """Response model for master data list"""
    success: bool
    data: List[MasterDataResponse]
    total: int
    page: int
    limit: int
    message: Optional[str] = None
