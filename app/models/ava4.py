"""
AVA4 device models
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AVA4Device(BaseModel):
    id: str
    mac_address: str
    device_name: Optional[str] = None
    status: str  # online, offline, maintenance
    patient_id: Optional[str] = None
    hospital_id: Optional[str] = None
    firmware_version: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AVA4DeviceCreate(BaseModel):
    device_id: str
    mac_address: str
    device_name: Optional[str] = None
    patient_id: Optional[str] = None
    hospital_id: Optional[str] = None
    location: Optional[str] = None

class AVA4DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    status: Optional[str] = None
    patient_id: Optional[str] = None
    hospital_id: Optional[str] = None
    location: Optional[str] = None

class AVA4VitalSigns(BaseModel):
    id: str
    device_id: str
    patient_id: str
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    oxygen_saturation: Optional[int] = None
    body_temperature: Optional[float] = None
    recorded_at: datetime
    created_at: Optional[datetime] = None
