"""
Master Data routes for Opera Panel
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.models.auth import User
from app.models.master_data import MasterDataCreate, MasterDataUpdate
from app.services.auth import get_current_user_optional
from app.services.stardust_api import stardust_api

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Add custom template filter for name extraction
def get_localized_name(name_data, language='en'):
    """Extract localized name from Stardust API name structure"""
    if isinstance(name_data, list):
        # Handle array format: [{"code": "th", "name": "..."}, {"code": "en", "name": "..."}]
        for item in name_data:
            if isinstance(item, dict) and item.get('code') == language:
                return item.get('name', '')
        # Fallback to first item if language not found
        if name_data and isinstance(name_data[0], dict):
            return name_data[0].get('name', '')
    elif isinstance(name_data, dict):
        # Handle object format: {"th": "...", "en": "..."}
        return name_data.get(language, name_data.get('en', ''))
    else:
        # Handle string format
        return str(name_data) if name_data else ''
    return ''

# Add the filter to Jinja environment
templates.env.filters['localized_name'] = get_localized_name

# Master Data Types Configuration
MASTER_DATA_TYPES = {
    "provinces": {
        "title": "Provinces",
        "title_th": "จังหวัด",
        "singular": "Province",
        "singular_th": "จังหวัด",
        "icon": "map-pin",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    },
    "districts": {
        "title": "Districts", 
        "title_th": "อำเภอ",
        "singular": "District",
        "singular_th": "อำเภอ",
        "icon": "map",
        "fields": ["name", "code", "province_code"],
        "required_fields": ["name", "code", "province_code"]
    },
    "sub-districts": {
        "title": "Sub-Districts",
        "title_th": "ตำบล",
        "singular": "Sub-District", 
        "singular_th": "ตำบล",
        "icon": "map-pin-2",
        "fields": ["name", "code", "province_code", "district_code", "postal_code"],
        "required_fields": ["name", "code", "province_code", "district_code"]
    },
    "hospital-types": {
        "title": "Hospital Types",
        "title_th": "ประเภทโรงพยาบาล",
        "singular": "Hospital Type",
        "singular_th": "ประเภทโรงพยาบาล",
        "icon": "building-hospital",
        "fields": ["name", "code", "description"],
        "required_fields": ["name", "code"]
    },
    "hospitals": {
        "title": "Hospitals",
        "title_th": "โรงพยาบาล", 
        "singular": "Hospital",
        "singular_th": "โรงพยาบาล",
        "icon": "building-plus",
        "fields": ["name", "code", "hospital_type_code", "address", "province_code", 
                  "district_code", "sub_district_code", "postal_code", "phone", "email"],
        "required_fields": ["name", "code"]
    },
    "departments": {
        "title": "Departments",
        "title_th": "แผนก",
        "singular": "Department",
        "singular_th": "แผนก",
        "icon": "building-store",
        "fields": ["name", "code", "description", "hospital_code"],
        "required_fields": ["name", "code"]
    },
    "specialties": {
        "title": "Medical Specialties",
        "title_th": "ความเชี่ยวชาญทางการแพทย์",
        "singular": "Specialty",
        "singular_th": "ความเชี่ยวชาญ",
        "icon": "stethoscope",
        "fields": ["name", "code", "description"],
        "required_fields": ["name", "code"]
    },
    "positions": {
        "title": "Staff Positions",
        "title_th": "ตำแหน่งงาน",
        "singular": "Position",
        "singular_th": "ตำแหน่ง",
        "icon": "user-check",
        "fields": ["name", "code", "description", "level"],
        "required_fields": ["name", "code"]
    },
    "device-types": {
        "title": "Device Types",
        "title_th": "ประเภทอุปกรณ์",
        "singular": "Device Type",
        "singular_th": "ประเภทอุปกรณ์",
        "icon": "device-desktop",
        "fields": ["name", "code", "description", "category"],
        "required_fields": ["name", "code"]
    },
    "manufacturers": {
        "title": "Manufacturers",
        "title_th": "ผู้ผลิต",
        "singular": "Manufacturer",
        "singular_th": "ผู้ผลิต",
        "icon": "building-factory",
        "fields": ["name", "code", "country", "contact_info"],
        "required_fields": ["name", "code"]
    },
    "insurance-types": {
        "title": "Insurance Types",
        "title_th": "ประเภทประกันสุขภาพ",
        "singular": "Insurance Type",
        "singular_th": "ประเภทประกันสุขภาพ",
        "icon": "shield-check",
        "fields": ["name", "code", "description", "coverage_details"],
        "required_fields": ["name", "code"]
    },
    "vital-sign-types": {
        "title": "Vital Sign Types",
        "title_th": "ประเภทสัญญาณชีพ",
        "singular": "Vital Sign Type",
        "singular_th": "ประเภทสัญญาณชีพ",
        "icon": "heartbeat",
        "fields": ["name", "code", "unit", "normal_range_min", "normal_range_max"],
        "required_fields": ["name", "code", "unit"]
    },
    "medication-categories": {
        "title": "Medication Categories",
        "title_th": "หมวดหมู่ยา",
        "singular": "Medication Category",
        "singular_th": "หมวดหมู่ยา",
        "icon": "pill",
        "fields": ["name", "code", "description"],
        "required_fields": ["name", "code"]
    },
    "appointment-types": {
        "title": "Appointment Types",
        "title_th": "ประเภทการนัดหมาย",
        "singular": "Appointment Type",
        "singular_th": "ประเภทการนัดหมาย",
        "icon": "calendar",
        "fields": ["name", "code", "description", "duration_minutes"],
        "required_fields": ["name", "code"]
    },
    "emergency-levels": {
        "title": "Emergency Levels",
        "title_th": "ระดับความฉุกเฉิน",
        "singular": "Emergency Level",
        "singular_th": "ระดับความฉุกเฉิน",
        "icon": "alert-triangle",
        "fields": ["name", "code", "description", "priority", "color"],
        "required_fields": ["name", "code", "priority"]
    },
    "patient-statuses": {
        "title": "Patient Statuses",
        "title_th": "สถานะผู้ป่วย",
        "singular": "Patient Status",
        "singular_th": "สถานะผู้ป่วย",
        "icon": "user-heart",
        "fields": ["name", "code", "description", "color"],
        "required_fields": ["name", "code"]
    },
    "room-types": {
        "title": "Room Types",
        "title_th": "ประเภทห้อง",
        "singular": "Room Type",
        "singular_th": "ประเภทห้อง",
        "icon": "door",
        "fields": ["name", "code", "description", "capacity"],
        "required_fields": ["name", "code"]
    },
    "languages": {
        "title": "Languages",
        "title_th": "ภาษา",
        "singular": "Language",
        "singular_th": "ภาษา",
        "icon": "language",
        "fields": ["name", "code", "native_name"],
        "required_fields": ["name", "code"]
    },
    "nationalities": {
        "title": "Nationalities",
        "title_th": "สัญชาติ",
        "singular": "Nationality",
        "singular_th": "สัญชาติ",
        "icon": "flag",
        "fields": ["name", "code", "country_code"],
        "required_fields": ["name", "code"]
    },
    "religions": {
        "title": "Religions",
        "title_th": "ศาสนา",
        "singular": "Religion",
        "singular_th": "ศาสนา",
        "icon": "star",
        "fields": ["name", "code", "description"],
        "required_fields": ["name", "code"]
    }
}

async def _check_auth(request: Request):
    """Check authentication helper"""
    token = request.session.get("access_token")
    if not token:
        return None, RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return None, RedirectResponse(url="/login")
    
    return user, token

@router.get("/master-data", response_class=HTMLResponse)
async def master_data_index(request: Request):
    """Master Data main page"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    return templates.TemplateResponse("admin/master_data/index.html", {
        "request": request,
        "user": user,
        "page_title": "Master Data Management",
        "master_data_types": MASTER_DATA_TYPES
    })

@router.get("/master-data/{data_type}", response_class=HTMLResponse)
async def master_data_list(request: Request, data_type: str, page: int = 1, search: Optional[str] = None,
                          province_code: Optional[str] = None, district_code: Optional[str] = None,
                          is_active: Optional[str] = None, date_from: Optional[str] = None, 
                          date_to: Optional[str] = None):
    """List master data records"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    limit = 20
    skip = (page - 1) * limit
    
    # Convert string parameters to integers, handling empty strings
    province_code_int = None
    district_code_int = None
    is_active_bool = None
    
    if province_code and province_code.strip():
        try:
            province_code_int = int(province_code)
        except ValueError:
            pass  # Keep as None if conversion fails
            
    if district_code and district_code.strip():
        try:
            district_code_int = int(district_code)
        except ValueError:
            pass  # Keep as None if conversion fails
    
    # Convert is_active filter
    if is_active and is_active.strip():
        if is_active.lower() in ['true', '1', 'active']:
            is_active_bool = True
        elif is_active.lower() in ['false', '0', 'inactive']:
            is_active_bool = False
    
    try:
        # For hospitals, fetch all data to ensure proper sorting, then paginate client-side
        if data_type == "hospitals":
            print(f"DEBUG: Fetching all hospital data for proper sorting")
            # Fetch all records first for proper sorting
            data_response = await stardust_api.get_master_data(
                token, data_type, 0, 1000, search, province_code_int, district_code_int,
                is_active_bool, date_from, date_to
            )
            print(f"DEBUG: Raw data response for hospitals (fetched up to 1000 records)")
            
            # Extract the actual data from the response
            if "data" in data_response and "data" in data_response["data"]:
                all_records = data_response["data"]["data"]
                total_count = data_response["data"].get("total", 0)
            elif "data" in data_response:
                all_records = data_response["data"]
                total_count = data_response.get("total", len(all_records) if isinstance(all_records, list) else 0)
            else:
                all_records = []
                total_count = 0
            
            print(f"DEBUG: Extracted {len(all_records) if isinstance(all_records, list) else 0} hospital records")
            
            # Sort all records by updated_at in descending order (most recent first)
            if isinstance(all_records, list) and all_records:
                print(f"DEBUG: Sorting {len(all_records)} hospital records by updated_at")
                def get_sort_date(record):
                    updated = record.get('updated_at')
                    created = record.get('created_at')
                    return updated if updated else (created if created else '')
                
                all_records = sorted(all_records, key=get_sort_date, reverse=True)
                print(f"DEBUG: Hospital records sorted - most recent first")
                
                # Now apply client-side pagination
                start_idx = skip
                end_idx = skip + limit
                records_data = all_records[start_idx:end_idx]
                print(f"DEBUG: Applied pagination: showing records {start_idx+1}-{min(end_idx, len(all_records))} of {len(all_records)}")
            else:
                records_data = []
                
        else:
            # For other data types, use normal pagination
            print(f"DEBUG: Fetching master data for {data_type} with params: skip={skip}, limit={limit}, search={search}")
            data_response = await stardust_api.get_master_data(
                token, data_type, skip, limit, search, province_code_int, district_code_int,
                is_active_bool, date_from, date_to
            )
            
            # Extract the actual data from the response
            if "data" in data_response and "data" in data_response["data"]:
                records_data = data_response["data"]["data"]
                total_count = data_response["data"].get("total", 0)
            elif "data" in data_response:
                records_data = data_response["data"]
                total_count = data_response.get("total", len(records_data) if isinstance(records_data, list) else 0)
            else:
                records_data = []
                total_count = 0
                
            print(f"DEBUG: Extracted {len(records_data) if isinstance(records_data, list) else 0} records, total: {total_count}")
        
        # Get reference data for dropdowns
        provinces = []
        districts = []
        hospital_types = []
        
        if data_type in ["districts", "sub-districts", "hospitals"]:
            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
            print(f"DEBUG: Raw provinces_response: {provinces_response}")
            
            # Handle nested structure for provinces
            if "data" in provinces_response and "data" in provinces_response["data"]:
                provinces = provinces_response["data"]["data"]
            elif "data" in provinces_response:
                provinces = provinces_response["data"]
            else:
                provinces = []
            print(f"DEBUG: Extracted {len(provinces)} provinces")
        
        # Load districts for sub-districts and hospitals pages
        if data_type in ["sub-districts", "hospitals"]:
            if province_code_int:
                # Load districts filtered by province for the dropdown filter
                districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code_int)
            else:
                # Load all districts for displaying district names in the table
                districts_response = await stardust_api.get_districts(token, 0, 1000, None)
                
            print(f"DEBUG: Raw districts_response: {districts_response}")
            
            # Handle nested structure for districts
            if "data" in districts_response and "data" in districts_response["data"]:
                districts = districts_response["data"]["data"]
            elif "data" in districts_response:
                districts = districts_response["data"]
            else:
                districts = []
            print(f"DEBUG: Extracted {len(districts)} districts")
            
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            print(f"DEBUG: Raw hospital_types_response: {hospital_types_response}")
            
            # Handle nested structure for hospital_types
            if "data" in hospital_types_response and "data" in hospital_types_response["data"]:
                hospital_types = hospital_types_response["data"]["data"]
            elif "data" in hospital_types_response:
                hospital_types = hospital_types_response["data"]
            else:
                hospital_types = []
            print(f"DEBUG: Extracted {len(hospital_types)} hospital_types")
        
        return templates.TemplateResponse("admin/master_data/list.html", {
            "request": request,
            "user": user,
            "page_title": f"{MASTER_DATA_TYPES[data_type]['title']} Management",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "records": records_data,
            "total": total_count,
            "page": page,
            "limit": limit,
            "search": search,
            "province_code": province_code,
            "district_code": district_code,
            "is_active": is_active,
            "date_from": date_from,
            "date_to": date_to,
            "provinces": provinces,
            "districts": districts,
            "hospital_types": hospital_types,
            "language": request.headers.get("Accept-Language", "en")[:2]
        })
        
    except HTTPException as e:
        return templates.TemplateResponse("admin/master_data/list.html", {
            "request": request,
            "user": user,
            "page_title": f"{MASTER_DATA_TYPES[data_type]['title']} Management",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "records": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "error": f"Failed to load data: {e.detail}",
            "provinces": [],
            "districts": [],
            "hospital_types": []
        })

@router.get("/master-data/{data_type}/new", response_class=HTMLResponse)
async def master_data_create_form(request: Request, data_type: str):
    """Create new master data record form"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    
    try:
        # Get reference data for dropdowns
        provinces = []
        districts = []
        hospital_types = []
        
        if data_type in ["districts", "sub-districts", "hospitals"]:
            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
            # Handle nested structure for provinces
            if "data" in provinces_response and "data" in provinces_response["data"]:
                provinces = provinces_response["data"]["data"]
            elif "data" in provinces_response:
                provinces = provinces_response["data"]
            else:
                provinces = []
        
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            # Handle nested structure for hospital_types
            if "data" in hospital_types_response and "data" in hospital_types_response["data"]:
                hospital_types = hospital_types_response["data"]["data"]
            elif "data" in hospital_types_response:
                hospital_types = hospital_types_response["data"]
            else:
                hospital_types = []
        
        return templates.TemplateResponse("admin/master_data/form.html", {
            "request": request,
            "user": user,
            "page_title": f"Create New {MASTER_DATA_TYPES[data_type]['singular']}",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "record": None,
            "is_edit": False,
            "provinces": provinces,
            "districts": districts,
            "hospital_types": hospital_types
        })
        
    except HTTPException as e:
        return templates.TemplateResponse("admin/master_data/form.html", {
            "request": request,
            "user": user,
            "page_title": f"Create New {MASTER_DATA_TYPES[data_type]['singular']}",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "record": None,
            "is_edit": False,
            "error": f"Failed to load form data: {e.detail}",
            "provinces": [],
            "districts": [],
            "hospital_types": []
        })

@router.get("/master-data/{data_type}/{record_id}/edit", response_class=HTMLResponse)
async def master_data_edit_form(request: Request, data_type: str, record_id: str):
    """Edit master data record form"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    
    try:
        # Get the record
        api_response = await stardust_api.get_master_data_record(token, data_type, record_id)
        
        # Extract the actual record from the API response
        if api_response.get("success") and "data" in api_response:
            if data_type == "hospitals" and "hospital" in api_response["data"]:
                record = api_response["data"]["hospital"]
            elif data_type == "provinces" and "province" in api_response["data"]:
                record = api_response["data"]["province"]
            elif data_type == "districts" and "district" in api_response["data"]:
                record = api_response["data"]["district"]
            elif data_type == "sub-districts" and "sub_district" in api_response["data"]:
                record = api_response["data"]["sub_district"]
            elif data_type == "hospital-types" and "hospital_type" in api_response["data"]:
                record = api_response["data"]["hospital_type"]
            else:
                # Fallback: try to get the data directly or use the first value
                data_content = api_response["data"]
                if isinstance(data_content, dict) and len(data_content) == 1:
                    record = list(data_content.values())[0]
                else:
                    record = data_content
        else:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Get reference data for dropdowns
        provinces = []
        districts = []
        hospital_types = []
        
        if data_type in ["districts", "sub-districts", "hospitals"]:
            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
            # Handle nested structure for provinces
            if "data" in provinces_response and "data" in provinces_response["data"]:
                provinces = provinces_response["data"]["data"]
            elif "data" in provinces_response:
                provinces = provinces_response["data"]
            else:
                provinces = []
        
        if data_type in ["sub-districts", "hospitals"] and record.get("province_code"):
            districts_response = await stardust_api.get_districts(token, 0, 1000, None, record.get("province_code"))
            # Handle nested structure for districts
            if "data" in districts_response and "data" in districts_response["data"]:
                districts = districts_response["data"]["data"]
            elif "data" in districts_response:
                districts = districts_response["data"]
            else:
                districts = []
            
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            # Handle nested structure for hospital_types
            if "data" in hospital_types_response and "data" in hospital_types_response["data"]:
                hospital_types = hospital_types_response["data"]["data"]
            elif "data" in hospital_types_response:
                hospital_types = hospital_types_response["data"]
            else:
                hospital_types = []
        
        return templates.TemplateResponse("admin/master_data/form.html", {
            "request": request,
            "user": user,
            "page_title": f"Edit {MASTER_DATA_TYPES[data_type]['singular']}",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "record": record,
            "is_edit": True,
            "provinces": provinces,
            "districts": districts,
            "hospital_types": hospital_types
        })
        
    except HTTPException as e:
        return RedirectResponse(url=f"/admin/master-data/{data_type}?error=Failed to load record: {e.detail}")

@router.get("/master-data/{data_type}/{record_id}", response_class=HTMLResponse)
async def master_data_detail(request: Request, data_type: str, record_id: str):
    """Detail view for master data record"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    # auth_result is the token when user is authenticated
    token = auth_result
    
    try:
        # Get the record
        print(f"DEBUG: Fetching {data_type} record with ID: {record_id}")
        api_response = await stardust_api.get_master_data_record(token, data_type, record_id)
        print(f"DEBUG: Fetched API response: {api_response}")
        
        # Extract the actual record from the API response
        if api_response.get("success") and "data" in api_response:
            if data_type == "hospitals" and "hospital" in api_response["data"]:
                record = api_response["data"]["hospital"]
            elif data_type == "provinces" and "province" in api_response["data"]:
                record = api_response["data"]["province"]
            elif data_type == "districts" and "district" in api_response["data"]:
                record = api_response["data"]["district"]
            elif data_type == "sub-districts" and "sub_district" in api_response["data"]:
                record = api_response["data"]["sub_district"]
            elif data_type == "hospital-types" and "hospital_type" in api_response["data"]:
                record = api_response["data"]["hospital_type"]
            else:
                # Fallback: try to get the data directly or use the first value
                data_content = api_response["data"]
                if isinstance(data_content, dict) and len(data_content) == 1:
                    record = list(data_content.values())[0]
                else:
                    record = data_content
        else:
            raise HTTPException(status_code=404, detail="Record not found")
            
        print(f"DEBUG: Extracted record: {record}")
        
        # Get related data for context display
        related_data = {}
        
        # For districts, get province info
        if data_type == "districts" and record.get("province_code"):
            try:
                provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                provinces = provinces_response.get("data", [])
                # Use string comparison for robustness
                province = next((p for p in provinces if str(p.get("code")) == str(record.get("province_code"))), None)
                if province:
                    related_data["province"] = province
            except Exception as e:
                print(f"Error loading province for district: {e}")
                pass
        
        # For sub-districts, get district and province info
        if data_type == "sub-districts":
            try:
                if record.get("district_code"):
                    districts_response = await stardust_api.get_districts(token, 0, 1000)
                    districts = districts_response.get("data", [])
                    # Use string comparison for robustness
                    district = next((d for d in districts if str(d.get("code")) == str(record.get("district_code"))), None)
                    if district:
                        related_data["district"] = district
                        
                        if district.get("province_code"):
                            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                            provinces = provinces_response.get("data", [])
                            # Use string comparison for robustness
                            province = next((p for p in provinces if str(p.get("code")) == str(district.get("province_code"))), None)
                            if province:
                                related_data["province"] = province
            except Exception as e:
                print(f"Error loading related data for sub-district: {e}")
                pass
        
        # For hospitals, get all location hierarchy and hospital type
        if data_type == "hospitals":
            try:
                if record.get("hospital_type_code"):
                    hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
                    hospital_types = hospital_types_response.get("data", [])
                    # Use string comparison for robustness
                    hospital_type = next((ht for ht in hospital_types if str(ht.get("code")) == str(record.get("hospital_type_code"))), None)
                    if hospital_type:
                        related_data["hospital_type"] = hospital_type
                
                # Try to get location hierarchy through sub_district_code first
                if record.get("sub_district_code"):
                    sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000)
                    sub_districts = sub_districts_response.get("data", [])
                    # Use string comparison for robustness
                    sub_district = next((sd for sd in sub_districts if str(sd.get("code")) == str(record.get("sub_district_code"))), None)
                    if sub_district:
                        related_data["sub_district"] = sub_district
                        
                        if sub_district.get("district_code"):
                            districts_response = await stardust_api.get_districts(token, 0, 1000)
                            districts = districts_response.get("data", [])
                            # Use string comparison for robustness
                            district = next((d for d in districts if str(d.get("code")) == str(sub_district.get("district_code"))), None)
                            if district:
                                related_data["district"] = district
                                
                                if district.get("province_code"):
                                    provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                                    provinces = provinces_response.get("data", [])
                                    # Use string comparison for robustness
                                    province = next((p for p in provinces if str(p.get("code")) == str(district.get("province_code"))), None)
                                    if province:
                                        related_data["province"] = province
                
                # If location hierarchy not found through sub_district, try direct district/province codes
                if not related_data.get("district") and record.get("district_code"):
                    districts_response = await stardust_api.get_districts(token, 0, 1000)
                    districts = districts_response.get("data", [])
                    # Use string comparison for robustness
                    district = next((d for d in districts if str(d.get("code")) == str(record.get("district_code"))), None)
                    if district:
                        related_data["district"] = district
                        
                        if district.get("province_code"):
                            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                            provinces = provinces_response.get("data", [])
                            # Use string comparison for robustness
                            province = next((p for p in provinces if str(p.get("code")) == str(district.get("province_code"))), None)
                            if province:
                                related_data["province"] = province
                
                # If still no province, try direct province code
                if not related_data.get("province") and record.get("province_code"):
                    provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                    provinces = provinces_response.get("data", [])
                    # Use string comparison for robustness
                    province = next((p for p in provinces if str(p.get("code")) == str(record.get("province_code"))), None)
                    if province:
                        related_data["province"] = province
                        
            except Exception as e:
                print(f"Error in hospital location lookup: {e}")
                pass
        
        return templates.TemplateResponse("admin/master_data/detail.html", {
            "request": request,
            "user": user,
            "page_title": f"{MASTER_DATA_TYPES[data_type]['singular']} Detail",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "record": record,
            "related_data": related_data,
            "language": request.headers.get("Accept-Language", "en")[:2]
        })
        
    except HTTPException as e:
        return RedirectResponse(url=f"/admin/master-data/{data_type}?error=Failed to load record: {e.detail}")

@router.post("/master-data/{data_type}")
async def master_data_create(request: Request, data_type: str):
    """Create new master data record"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    
    try:
        form_data = await request.form()
        
        # Build the data object
        data = {
            "data_type": data_type,
            "name": {
                "en": form_data.get("name_en", ""),
                "th": form_data.get("name_th", "")
            },
            "code": form_data.get("code", ""),
            "is_active": form_data.get("is_active") == "on"
        }
        
        # Add type-specific fields
        province_code_str = form_data.get("province_code")
        if data_type in ["districts", "sub-districts", "hospitals"] and province_code_str:
            data["province_code"] = int(str(province_code_str))
        
        district_code_str = form_data.get("district_code")
        if data_type in ["sub-districts", "hospitals"] and district_code_str:
            data["district_code"] = int(str(district_code_str))
        
        if data_type == "sub-districts" and form_data.get("postal_code"):
            data["additional_fields"] = {"postal_code": form_data.get("postal_code")}
        
        if data_type == "hospital-types" and form_data.get("description_en"):
            data["additional_fields"] = {
                "description": {
                    "en": form_data.get("description_en", ""),
                    "th": form_data.get("description_th", "")
                }
            }
        
        if data_type == "hospitals":
            additional_fields = {}
            if form_data.get("hospital_type_code"):
                additional_fields["hospital_type_code"] = form_data.get("hospital_type_code")
            if form_data.get("address"):
                additional_fields["address"] = form_data.get("address")
            if form_data.get("postal_code"):
                additional_fields["postal_code"] = form_data.get("postal_code")
            if form_data.get("phone"):
                additional_fields["phone"] = form_data.get("phone")
            if form_data.get("email"):
                additional_fields["email"] = form_data.get("email")
            
            sub_district_code_str = form_data.get("sub_district_code")
            if sub_district_code_str:
                data["sub_district_code"] = int(str(sub_district_code_str))
            
            if additional_fields:
                data["additional_fields"] = additional_fields
        
        # Create the record
        result = await stardust_api.create_master_data(token, data)
        
        return RedirectResponse(url=f"/admin/master-data/{data_type}?success=Record created successfully", status_code=303)
        
    except HTTPException as e:
        return RedirectResponse(url=f"/admin/master-data/{data_type}/new?error=Failed to create record: {e.detail}", status_code=303)

@router.post("/master-data/{data_type}/{record_id}/update")
async def master_data_update(request: Request, data_type: str, record_id: str):
    """Update master data record"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    
    try:
        form_data = await request.form()
        
        # Build the update data object
        data = {
            "name": {
                "en": form_data.get("name_en", ""),
                "th": form_data.get("name_th", "")
            },
            "code": form_data.get("code", ""),
            "is_active": form_data.get("is_active") == "on"
        }
        
        # Add type-specific fields
        province_code_str = form_data.get("province_code")
        if data_type in ["districts", "sub-districts", "hospitals"] and province_code_str:
            data["province_code"] = int(str(province_code_str))
        
        district_code_str = form_data.get("district_code")
        if data_type in ["sub-districts", "hospitals"] and district_code_str:
            data["district_code"] = int(str(district_code_str))
        
        if data_type == "sub-districts" and form_data.get("postal_code"):
            data["additional_fields"] = {"postal_code": form_data.get("postal_code")}
        
        if data_type == "hospital-types" and form_data.get("description_en"):
            data["additional_fields"] = {
                "description": {
                    "en": form_data.get("description_en", ""),
                    "th": form_data.get("description_th", "")
                }
            }
        
        if data_type == "hospitals":
            additional_fields = {}
            if form_data.get("hospital_type_code"):
                additional_fields["hospital_type_code"] = form_data.get("hospital_type_code")
            if form_data.get("address"):
                additional_fields["address"] = form_data.get("address")
            if form_data.get("postal_code"):
                additional_fields["postal_code"] = form_data.get("postal_code")
            if form_data.get("phone"):
                additional_fields["phone"] = form_data.get("phone")
            if form_data.get("email"):
                additional_fields["email"] = form_data.get("email")
            
            sub_district_code_str = form_data.get("sub_district_code")
            if sub_district_code_str:
                data["sub_district_code"] = int(str(sub_district_code_str))
            
            if additional_fields:
                data["additional_fields"] = additional_fields
        
        # Update the record
        result = await stardust_api.update_master_data(token, data_type, record_id, data)
        
        return RedirectResponse(url=f"/admin/master-data/{data_type}?success=Record updated successfully", status_code=303)
        
    except HTTPException as e:
        return RedirectResponse(url=f"/admin/master-data/{data_type}/{record_id}/edit?error=Failed to update record: {e.detail}", status_code=303)

@router.post("/master-data/{data_type}/{record_id}/delete")
async def master_data_delete(request: Request, data_type: str, record_id: str):
    """Delete master data record"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    
    try:
        # Delete the record
        result = await stardust_api.delete_master_data(token, data_type, record_id)
        
        return RedirectResponse(url=f"/admin/master-data/{data_type}?success=Record deleted successfully", status_code=303)
        
    except HTTPException as e:
        return RedirectResponse(url=f"/admin/master-data/{data_type}?error=Failed to delete record: {e.detail}", status_code=303)

# API endpoints for AJAX requests
@router.get("/api/master-data/provinces")
async def get_provinces(request: Request):
    """Get all provinces (AJAX endpoint)"""
    user, auth_result = await _check_auth(request)
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    token = auth_result
    if not isinstance(token, str):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        provinces_response = await stardust_api.get_provinces(token, 0, 1000)
        provinces_data = provinces_response.get("data", {}).get("data", [])
        return JSONResponse({"data": provinces_data})
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)

@router.get("/api/master-data/districts/{province_code}")
async def get_districts_by_province(request: Request, province_code: int):
    """Get districts by province code (AJAX endpoint)"""
    user, auth_result = await _check_auth(request)
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    token = auth_result
    if not isinstance(token, str):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code)
        districts_data = districts_response.get("data", {}).get("data", [])
        return JSONResponse({"data": districts_data})
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)

@router.get("/api/master-data/sub-districts/{district_code}")
async def get_sub_districts_by_district(request: Request, district_code: int):
    """Get sub-districts by district code (AJAX endpoint)"""
    user, auth_result = await _check_auth(request)
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    token = auth_result
    if not isinstance(token, str):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000, None, None, district_code)
        sub_districts_data = sub_districts_response.get("data", {}).get("data", [])
        return JSONResponse({"data": sub_districts_data})
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)

@router.post("/admin/master-data/hospitals/{record_id}/update-location")
async def update_hospital_location(request: Request, record_id: str):
    """Update hospital location and address from Google Maps"""
    user, auth_result = await _check_auth(request)
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    token = auth_result
    if not isinstance(token, str):
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    try:
        # Get the request data
        import json
        body = await request.body()
        location_data = json.loads(body)
        
        # Validate required fields
        if not location_data.get("location") or len(location_data["location"]) != 2:
            return JSONResponse({"error": "Invalid location coordinates"}, status_code=400)
        
        # Prepare update data for Stardust API
        update_data = {
            "location": location_data["location"]  # [lat, lng]
        }
        
        # If we have formatted address, we could store it in a custom field
        # Note: The current hospital schema may not have an address field in Stardust
        # But we can still update the location coordinates
        
        # Update the record via Stardust API
        result = await stardust_api.update_master_data(token, "hospitals", record_id, update_data)
        
        return JSONResponse({
            "success": True, 
            "message": "Hospital location updated successfully",
            "data": {
                "location": location_data["location"],
                "formatted_address": location_data.get("formatted_address")
            }
        })
        
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse({"error": f"Failed to update location: {str(e)}"}, status_code=500)
