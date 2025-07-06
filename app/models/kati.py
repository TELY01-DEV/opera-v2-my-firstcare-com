"""
Kati device models for Opera Panel
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class KatiDevice(BaseModel):
    id: str
    imei: str
    device_name: Optional[str] = None
    patient_id: Optional[str] = None
    hospital_id: Optional[str] = None
    status: str  # online, offline, maintenance
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[int] = None
    location: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class KatiVitalSigns(BaseModel):
    device_id: str
    patient_id: str
    timestamp: datetime
    heart_rate: Optional[int] = None
    steps: Optional[int] = None
    distance: Optional[float] = None
    calories_burned: Optional[int] = None
    sleep_duration: Optional[int] = None
    activity_level: Optional[str] = None

class KatiDeviceCreate(BaseModel):
    imei: str
    device_name: Optional[str] = None
    patient_id: Optional[str] = None
    hospital_id: Optional[str] = None
    location: Optional[str] = None

class KatiDeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    patient_id: Optional[str] = None
    hospital_id: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
