"""
Patient models for Opera Panel
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

class Patient(BaseModel):
    id: str
    patient_id: str  # Hospital patient ID
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str  # male, female, other
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    hospital_id: Optional[str] = None
    ava_mac_address: Optional[str] = None
    watch_mac_address: Optional[str] = None
    medical_record_number: Optional[str] = None
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PatientCreate(BaseModel):
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    hospital_id: Optional[str] = None
    medical_record_number: Optional[str] = None

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    ava_mac_address: Optional[str] = None
    watch_mac_address: Optional[str] = None
    is_active: Optional[bool] = None

class PatientVitals(BaseModel):
    patient_id: str
    device_type: str  # ava4, kati
    timestamp: datetime
    vital_signs: dict  # Flexible structure for different vital signs
