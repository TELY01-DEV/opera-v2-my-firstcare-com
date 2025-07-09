"""
API routes for Opera Panel CRUD operations
"""
from fastapi import APIRouter, Request, HTTPException, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional

from app.models.auth import User
from app.models.patient import PatientCreate, PatientUpdate
from app.models.ava4 import AVA4DeviceCreate, AVA4DeviceUpdate
from app.models.kati import KatiDeviceCreate, KatiDeviceUpdate
from app.models.qube_vital import QubeVitalDeviceCreate, QubeVitalDeviceUpdate
from app.services.auth import get_current_user_optional
from app.services.stardust_api import stardust_api

router = APIRouter()

# ===============================
# PATIENT CRUD OPERATIONS
# ===============================

@router.post("/patients")
async def create_patient(
    request: Request,
    patient_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    medical_record_number: Optional[str] = Form(None)
):
    """Create new patient"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        # Prepare patient data
        patient_data = {
            "patient_id": patient_id,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "phone": phone,
            "email": email,
            "address": address,
            "medical_record_number": medical_record_number,
            "is_active": True
        }
        
        # Remove None values
        patient_data = {k: v for k, v in patient_data.items() if v is not None}
        
        # Create patient via Stardust API
        result = await stardust_api.create_patient(token, patient_data)
        
        # Redirect back to patients list
        return RedirectResponse(url="/admin/patients", status_code=302)
        
    except HTTPException as e:
        # Redirect with error
        return RedirectResponse(url=f"/admin/patients?error={e.detail}", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/admin/patients?error=Failed to create patient", status_code=302)

@router.put("/patients/{patient_id}")
async def update_patient(
    patient_id: str,
    request: Request,
    patient_data: PatientUpdate
):
    """Update patient"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.update_patient(token, patient_id, patient_data.dict(exclude_unset=True))
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: str,
    request: Request
):
    """Delete patient"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.delete_patient(token, patient_id)
        return {"status": "success", "message": "Patient deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# AVA4 DEVICE CRUD OPERATIONS
# ===============================

@router.post("/devices/ava4")
async def create_ava4_device(
    request: Request,
    device_id: str = Form(...),
    mac_address: str = Form(...),
    location: Optional[str] = Form(None),
    hospital_id: Optional[str] = Form(None),
    patient_id: Optional[str] = Form(None)
):
    """Create new AVA4 device"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        device_data = {
            "device_id": device_id,
            "mac_address": mac_address,
            "location": location,
            "hospital_id": hospital_id,
            "patient_id": patient_id,
            "status": "active",
            "device_type": "ava4"
        }
        
        # Remove None values
        device_data = {k: v for k, v in device_data.items() if v is not None}
        
        # Create device via Stardust API
        result = await stardust_api.create_ava4_device(token, device_data)
        
        return RedirectResponse(url="/devices/ava4", status_code=302)
        
    except HTTPException as e:
        return RedirectResponse(url=f"/devices/ava4?error={e.detail}", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/devices/ava4?error=Failed to create device", status_code=302)

@router.put("/devices/ava4/{device_id}")
async def update_ava4_device(
    device_id: str,
    request: Request,
    device_data: AVA4DeviceUpdate
):
    """Update AVA4 device"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.update_ava4_device(token, device_id, device_data.dict(exclude_unset=True))
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/devices/ava4/{device_id}")
async def delete_ava4_device(
    device_id: str,
    request: Request
):
    """Delete AVA4 device"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.delete_ava4_device(token, device_id)
        return {"status": "success", "message": "Device deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# KATI DEVICE CRUD OPERATIONS
# ===============================

@router.post("/devices/kati")
async def create_kati_device(
    request: Request,
    device_id: str = Form(...),
    imei: str = Form(...),
    patient_id: Optional[str] = Form(None),
    hospital_id: Optional[str] = Form(None)
):
    """Create new Kati device"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        device_data = {
            "device_id": device_id,
            "imei": imei,
            "patient_id": patient_id,
            "hospital_id": hospital_id,
            "status": "active",
            "device_type": "kati"
        }
        
        # Remove None values
        device_data = {k: v for k, v in device_data.items() if v is not None}
        
        # Create device via Stardust API
        result = await stardust_api.create_kati_device(token, device_data)
        
        return RedirectResponse(url="/devices/kati", status_code=302)
        
    except HTTPException as e:
        return RedirectResponse(url=f"/devices/kati?error={e.detail}", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/devices/kati?error=Failed to create device", status_code=302)

@router.put("/devices/kati/{device_id}")
async def update_kati_device(
    device_id: str,
    request: Request,
    device_data: KatiDeviceUpdate
):
    """Update Kati device"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.update_kati_device(token, device_id, device_data.dict(exclude_unset=True))
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/devices/kati/{device_id}")
async def delete_kati_device(
    device_id: str,
    request: Request
):
    """Delete Kati device"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.delete_kati_device(token, device_id)
        return {"status": "success", "message": "Device deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# QUBE-VITAL DEVICE CRUD OPERATIONS
# ===============================

@router.post("/devices/qube-vital")
async def create_qube_vital_device(
    request: Request,
    device_id: str = Form(...),
    imei: str = Form(...),
    hospital_id: Optional[str] = Form(None),
    location: Optional[str] = Form(None)
):
    """Create new Qube-Vital device"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        device_data = {
            "device_id": device_id,
            "imei": imei,
            "hospital_id": hospital_id,
            "location": location,
            "status": "active",
            "device_type": "qube_vital"
        }
        
        # Remove None values
        device_data = {k: v for k, v in device_data.items() if v is not None}
        
        # Create device via Stardust API
        result = await stardust_api.create_qube_vital_device(token, device_data)
        
        return RedirectResponse(url="/devices/qube-vital", status_code=302)
        
    except HTTPException as e:
        return RedirectResponse(url=f"/devices/qube-vital?error={e.detail}", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/devices/qube-vital?error=Failed to create device", status_code=302)

@router.put("/devices/qube-vital/{device_id}")
async def update_qube_vital_device(
    device_id: str,
    request: Request,
    device_data: QubeVitalDeviceUpdate
):
    """Update Qube-Vital device"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.update_qube_vital_device(token, device_id, device_data.dict(exclude_unset=True))
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/devices/qube-vital/{device_id}")
async def delete_qube_vital_device(
    device_id: str,
    request: Request
):
    """Delete Qube-Vital device"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        result = await stardust_api.delete_qube_vital_device(token, device_id)
        return {"status": "success", "message": "Device deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# MASTER DATA DROPDOWN OPERATIONS
# ===============================

@router.get("/master-data/provinces")
async def get_provinces_dropdown(request: Request):
    """Get provinces for dropdown"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        provinces_response = await stardust_api.get_provinces(token, 0, 1000)
        
        # Handle nested structure for provinces
        if "data" in provinces_response and "provinces" in provinces_response["data"]:
            provinces = provinces_response["data"]["provinces"]
        elif "data" in provinces_response and "data" in provinces_response["data"]:
            provinces = provinces_response["data"]["data"]
        elif "data" in provinces_response:
            provinces = provinces_response["data"]
        else:
            provinces = []
        
        # Normalize data structure
        normalized_provinces = []
        for province in provinces:
            if isinstance(province, dict):
                normalized_province = province.copy()
                # Convert en_name/th_name to name structure
                if 'en_name' in province and 'th_name' in province:
                    normalized_province['name'] = {
                        'en': province['en_name'],
                        'th': province['th_name']
                    }
                normalized_provinces.append(normalized_province)
            else:
                normalized_provinces.append(province)
        
        return JSONResponse(content={"data": normalized_provinces})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/master-data/districts/{province_code}")
async def get_districts_dropdown(request: Request, province_code: int):
    """Get districts for dropdown by province"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code)
        
        # Handle nested structure for districts
        if "data" in districts_response and "districts" in districts_response["data"]:
            districts = districts_response["data"]["districts"]
        elif "data" in districts_response and "data" in districts_response["data"]:
            districts = districts_response["data"]["data"]
        elif "data" in districts_response:
            districts = districts_response["data"]
        else:
            districts = []
        
        # Normalize data structure
        normalized_districts = []
        for district in districts:
            if isinstance(district, dict):
                normalized_district = district.copy()
                # Convert en_name/th_name to name structure
                if 'en_name' in district and 'th_name' in district:
                    normalized_district['name'] = {
                        'en': district['en_name'],
                        'th': district['th_name']
                    }
                normalized_districts.append(normalized_district)
            else:
                normalized_districts.append(district)
        
        return JSONResponse(content={"data": normalized_districts})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/master-data/sub-districts/{district_code}")
async def get_sub_districts_dropdown(request: Request, district_code: int, province_code: int):
    """Get sub-districts for dropdown by district and province"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000, None, province_code, district_code)
        
        # Handle nested structure for sub-districts
        if "data" in sub_districts_response and "sub_districts" in sub_districts_response["data"]:
            sub_districts = sub_districts_response["data"]["sub_districts"]
        elif "data" in sub_districts_response and "data" in sub_districts_response["data"]:
            sub_districts = sub_districts_response["data"]["data"]
        elif "data" in sub_districts_response:
            sub_districts = sub_districts_response["data"]
        else:
            sub_districts = []
        
        # Normalize data structure
        normalized_sub_districts = []
        for sub_district in sub_districts:
            if isinstance(sub_district, dict):
                normalized_sub_district = sub_district.copy()
                # Convert en_name/th_name to name structure
                if 'en_name' in sub_district and 'th_name' in sub_district:
                    normalized_sub_district['name'] = {
                        'en': sub_district['en_name'],
                        'th': sub_district['th_name']
                    }
                normalized_sub_districts.append(normalized_sub_district)
            else:
                normalized_sub_districts.append(sub_district)
        
        return JSONResponse(content={"data": normalized_sub_districts})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
