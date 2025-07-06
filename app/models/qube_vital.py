"""
Qube-Vital device models for Opera Panel
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class QubeVitalDevice(BaseModel):
    id: str
    imei: str
    device_name: Optional[str] = None
    hospital_id: Optional[str] = None
    room_number: Optional[str] = None
    status: str  # online, offline, maintenance
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    location: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class QubeVitalData(BaseModel):
    device_id: str
    hospital_id: str
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[int] = None
    noise_level: Optional[float] = None
    occupancy: Optional[bool] = None
    patient_proximity: Optional[bool] = None

class QubeVitalDeviceCreate(BaseModel):
    imei: str
    device_name: Optional[str] = None
    hospital_id: Optional[str] = None
    room_number: Optional[str] = None
    location: Optional[str] = None

class QubeVitalDeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    hospital_id: Optional[str] = None
    room_number: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
