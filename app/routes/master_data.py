"""
Master Data routes for Opera Panel
"""
import json
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.models.auth import User
from app.models.master_data import MasterDataCreate, MasterDataUpdate
from app.services.auth import get_current_user_optional, get_valid_token, get_current_user_with_refresh
from app.services.stardust_api import stardust_api

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Add custom template filter for name extraction
def get_localized_name(name_data, language='en'):
    """Extract localized name from Stardust API name structure"""
    if isinstance(name_data, dict):
        # Handle new structure from API with en_name/th_name
        if 'en_name' in name_data and 'th_name' in name_data:
            return name_data.get('th_name') if language == 'th' else name_data.get('en_name', name_data.get('th_name', ''))
        # Handle object format: {"th": "...", "en": "..."}  
        elif language in name_data:
            return name_data[language]
        elif 'en' in name_data:
            return name_data['en']
        else:
            return str(name_data)
    elif isinstance(name_data, list):
        # Handle array format: [{"code": "th", "name": "..."}, {"code": "en", "name": "..."}]
        for item in name_data:
            if isinstance(item, dict) and item.get('code') == language:
                return item.get('name', '')
        # Fallback to first item if language not found
        if name_data and isinstance(name_data[0], dict):
            return name_data[0].get('name', '')
    else:
        # Handle string format
        return str(name_data) if name_data else ''
    return ''

# Add the filter to Jinja environment
templates.env.filters['localized_name'] = get_localized_name

# Normalize data structure for consistent use in templates
def normalize_location_data(data_list):
    """Normalize location data to have consistent name structure"""
    normalized = []
    for item in data_list:
        if isinstance(item, dict):
            normalized_item = item.copy()
            # Convert en_name/th_name to name structure
            if 'en_name' in item and 'th_name' in item:
                normalized_item['name'] = {
                    'en': item['en_name'],
                    'th': item['th_name']
                }
            normalized.append(normalized_item)
        else:
            normalized.append(item)
    return normalized

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
    },
    "blood_groups": {
        "title": "Blood Groups",
        "title_th": "กรุ๊ปเลือด", 
        "singular": "Blood Group",
        "singular_th": "กรุ๊ปเลือด",
        "icon": "droplet",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    },
    "nations": {
        "title": "Nations",
        "title_th": "ประเทศ",
        "singular": "Nation", 
        "singular_th": "ประเทศ",
        "icon": "flag",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    },
    "human_skin_colors": {
        "title": "Human Skin Colors",
        "title_th": "สีผิว",
        "singular": "Skin Color",
        "singular_th": "สีผิว", 
        "icon": "palette",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    },
    "ward_lists": {
        "title": "Hospital Wards",
        "title_th": "หอผู้ป่วย",
        "singular": "Ward",
        "singular_th": "หอผู้ป่วย",
        "icon": "building-hospital",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    },
    "staff_types": {
        "title": "Staff Types", 
        "title_th": "ประเภทเจ้าหน้าที่",
        "singular": "Staff Type",
        "singular_th": "ประเภทเจ้าหน้าที่",
        "icon": "users",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    },
    "underlying_diseases": {
        "title": "Underlying Diseases",
        "title_th": "โรคประจำตัว",
        "singular": "Underlying Disease", 
        "singular_th": "โรคประจำตัว",
        "icon": "heart-pulse",
        "fields": ["name", "code"],
        "required_fields": ["name", "code"]
    }
}

async def _check_auth(request: Request):
    """Check authentication helper with token refresh"""
    user = await get_current_user_with_refresh(request)
    if not user:
        return None, RedirectResponse(url="/login")
    
    token = await get_valid_token(request)
    if not token:
        return None, RedirectResponse(url="/login")
    
    return user, token

async def _check_auth_api(request: Request):
    """Check authentication helper for API endpoints with token refresh"""
    user = await get_current_user_with_refresh(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = await get_valid_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return user, token
    
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
                          sub_district_code: Optional[str] = None, status: Optional[str] = None, 
                          date_from: Optional[str] = None, date_to: Optional[str] = None, 
                          limit: int = 25, skip: Optional[int] = None):
    """List master data records"""
    user, auth_result = await _check_auth(request)
    if not user:
        return auth_result
    
    if data_type not in MASTER_DATA_TYPES:
        raise HTTPException(status_code=404, detail="Master data type not found")
    
    token = auth_result
    if not isinstance(token, str):
        return auth_result
    
    # Handle pagination - use skip if provided, otherwise calculate from page
    if skip is not None:
        actual_skip = skip
        actual_page = (skip // limit) + 1
    else:
        actual_skip = (page - 1) * limit
        actual_page = page
    
    # Convert string parameters to integers, handling empty strings
    province_code_int = None
    district_code_int = None
    sub_district_code_int = None
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
    
    if sub_district_code and sub_district_code.strip():
        try:
            sub_district_code_int = int(sub_district_code)
        except ValueError:
            pass  # Keep as None if conversion fails
    
    # Convert is_active filter - be more explicit about the conversion
    if status and status.strip():
        is_active_str = status.strip().lower()
        if is_active_str in ['true', '1', 'active', 'yes']:
            is_active_bool = True
        elif is_active_str in ['false', '0', 'inactive', 'no']:
            is_active_bool = False
        else:
            is_active_bool = None  # Invalid value, don't filter
    else:
        is_active_bool = None
    
    print(f"DEBUG: is_active conversion: '{status}' -> {is_active_bool}")
    
    try:
        # For hospitals, fetch all data to ensure proper sorting, then paginate client-side
        if data_type == "hospitals":
            # Fetch all records first for proper sorting
            data_response = await stardust_api.get_master_data(
                token, data_type, 0, 1000, search, province_code_int, district_code_int,
                sub_district_code_int, is_active_bool, date_from, date_to
            )
            
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
            
            # Sort all records by updated_at in descending order (most recent first)
            if isinstance(all_records, list) and all_records:
                def get_sort_date(record):
                    updated = record.get('updated_at')
                    created = record.get('created_at')
                    return updated if updated else (created if created else '')

                all_records = sorted(all_records, key=get_sort_date, reverse=True)
                
                # Apply client-side status filtering if the API doesn't support it
                if is_active_bool is not None:
                    print(f"DEBUG: Applying client-side status filtering for is_active={is_active_bool}")
                    print(f"DEBUG: Total records before filtering: {len(all_records)}")
                    
                    # Debug: Check what is_active values we actually have
                    active_values = {}
                    for record in all_records[:10]:  # Check first 10 records
                        is_active_value = record.get('is_active')
                        if is_active_value not in active_values:
                            active_values[is_active_value] = 0
                        active_values[is_active_value] += 1
                    print(f"DEBUG: Sample is_active values in data: {active_values}")
                    
                    filtered_records = []
                    none_count = 0
                    matched_count = 0
                    
                    for record in all_records:
                        # Check if record is active/inactive based on is_active field
                        record_is_active = record.get('is_active')
                        
                        # Handle different possible values
                        if record_is_active is None:
                            # If no is_active field, treat as inactive (False) by default
                            record_is_active = False
                            none_count += 1
                        elif isinstance(record_is_active, str):
                            # Handle string values
                            record_is_active = record_is_active.lower() in ['true', '1', 'active', 'yes']
                        elif isinstance(record_is_active, bool):
                            # Already a boolean, use as is
                            pass
                        else:
                            # Unknown type, treat as inactive
                            record_is_active = False
                            
                        if record_is_active == is_active_bool:
                            filtered_records.append(record)
                            matched_count += 1
                            
                    print(f"DEBUG: Records with None is_active: {none_count}")
                    print(f"DEBUG: Records matching filter: {matched_count}")
                    all_records = filtered_records
                    print(f"DEBUG: After client-side filtering: {len(all_records)} records")
                
                # Update total count after filtering
                total_count = len(all_records)
                
                # Now apply client-side pagination
                start_idx = actual_skip
                end_idx = actual_skip + limit
                records_data = all_records[start_idx:end_idx]
            else:
                records_data = []
                
        else:
            # For other data types, use normal pagination
            data_response = await stardust_api.get_master_data(
                token, data_type, actual_skip, limit, search, province_code_int, district_code_int,
                sub_district_code_int, is_active_bool, date_from, date_to
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
        
        # Get reference data for dropdowns
        provinces = []
        districts = []
        sub_districts = []
        hospital_types = []
        
        if data_type in ["districts", "sub-districts", "hospitals"]:
            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
            print(f"DEBUG: Provinces response structure: {list(provinces_response.keys()) if provinces_response else 'None'}")
            
            # Handle nested structure for provinces
            if "data" in provinces_response and "provinces" in provinces_response["data"]:
                provinces = provinces_response["data"]["provinces"]
                print(f"DEBUG: Using provinces from data.provinces - count: {len(provinces)}")
            elif "data" in provinces_response and "data" in provinces_response["data"]:
                provinces = provinces_response["data"]["data"]
                print(f"DEBUG: Using provinces from data.data - count: {len(provinces)}")
            elif "data" in provinces_response:
                provinces = provinces_response["data"]
                print(f"DEBUG: Using provinces from data - count: {len(provinces)}")
            else:
                provinces = []
                print(f"DEBUG: No provinces found in response")
                
            # Normalize provinces data for template
            provinces = normalize_location_data(provinces)
            print(f"DEBUG: Normalized provinces count: {len(provinces)}")
            if provinces:
                print(f"DEBUG: First normalized province: {provinces[0]}")
        
        # Load districts for sub-districts and hospitals pages
        if data_type in ["sub-districts", "hospitals"]:
            if province_code_int:
                # Load districts filtered by province for the dropdown filter
                districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code_int)
                
                # Handle nested structure for districts
                if "data" in districts_response and "districts" in districts_response["data"]:
                    districts = districts_response["data"]["districts"]
                elif "data" in districts_response and "data" in districts_response["data"]:
                    districts = districts_response["data"]["data"]
                elif "data" in districts_response:
                    districts = districts_response["data"]
                else:
                    districts = []
                    
                # Normalize districts data for template
                districts = normalize_location_data(districts)
            else:
                # For hospitals page, load ALL districts initially so table can show district names
                if data_type == "hospitals":
                    try:
                        # Get all provinces to fetch all districts
                        all_districts = []
                        for province in provinces:
                            province_code = province.get('code')
                            if province_code:
                                try:
                                    province_code_int = int(province_code)
                                    districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code_int)
                                    
                                    # Handle nested structure for districts
                                    if "data" in districts_response and "districts" in districts_response["data"]:
                                        province_districts = districts_response["data"]["districts"]
                                    elif "data" in districts_response and "data" in districts_response["data"]:
                                        province_districts = districts_response["data"]["data"]
                                    elif "data" in districts_response:
                                        province_districts = districts_response["data"]
                                    else:
                                        province_districts = []
                                    
                                    all_districts.extend(province_districts)
                                except (ValueError, Exception) as e:
                                    print(f"DEBUG: Error loading districts for province {province_code}: {e}")
                                    continue
                        
                        districts = normalize_location_data(all_districts)
                        print(f"DEBUG: Loaded all districts for table display: {len(districts)}")
                    except Exception as e:
                        print(f"DEBUG: Error loading all districts: {e}")
                        districts = []
                else:
                    districts = []
            
        # Load sub-districts for hospitals pages
        if data_type == "hospitals":
            if province_code_int and district_code_int:
                # Load sub-districts filtered by province and district for the dropdown filter
                sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000, None, province_code_int, district_code_int)
                
                # Handle nested structure for sub-districts
                if "data" in sub_districts_response and "sub_districts" in sub_districts_response["data"]:
                    sub_districts = sub_districts_response["data"]["sub_districts"]
                elif "data" in sub_districts_response and "data" in sub_districts_response["data"]:
                    sub_districts = sub_districts_response["data"]["data"]
                elif "data" in sub_districts_response:
                    sub_districts = sub_districts_response["data"]
                else:
                    sub_districts = []
                    
                # Normalize sub-districts data for template
                sub_districts = normalize_location_data(sub_districts)
            else:
                # Load ALL sub-districts for table display
                try:
                    all_sub_districts = []
                    for district in districts:
                        district_code = district.get('code')
                        district_province_code = district.get('province_code')
                        if district_code and district_province_code:
                            try:
                                district_code_int = int(district_code)
                                province_code_int = int(district_province_code)
                                sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000, None, province_code_int, district_code_int)
                                
                                # Handle nested structure for sub-districts
                                if "data" in sub_districts_response and "sub_districts" in sub_districts_response["data"]:
                                    district_sub_districts = sub_districts_response["data"]["sub_districts"]
                                elif "data" in sub_districts_response and "data" in sub_districts_response["data"]:
                                    district_sub_districts = sub_districts_response["data"]["data"]
                                elif "data" in sub_districts_response:
                                    district_sub_districts = sub_districts_response["data"]
                                else:
                                    district_sub_districts = []
                                
                                all_sub_districts.extend(district_sub_districts)
                            except (ValueError, Exception) as e:
                                print(f"DEBUG: Error loading sub-districts for district {district_code}: {e}")
                                continue
                    
                    sub_districts = normalize_location_data(all_sub_districts)
                    print(f"DEBUG: Loaded all sub-districts for table display: {len(sub_districts)}")
                except Exception as e:
                    print(f"DEBUG: Error loading all sub-districts: {e}")
                    sub_districts = []
        
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            
            # Handle nested structure for hospital_types
            if "data" in hospital_types_response and "hospital_types" in hospital_types_response["data"]:
                hospital_types = hospital_types_response["data"]["hospital_types"]
            elif "data" in hospital_types_response and "data" in hospital_types_response["data"]:
                hospital_types = hospital_types_response["data"]["data"]
            elif "data" in hospital_types_response:
                hospital_types = hospital_types_response["data"]
            else:
                hospital_types = []
                
            # Normalize hospital types data for template
            hospital_types = normalize_location_data(hospital_types)
        
        # Normalize data structure for consistent use in templates
        provinces = normalize_location_data(provinces)
        districts = normalize_location_data(districts)
        sub_districts = normalize_location_data(sub_districts)
        
        # Debug output for dropdown data
        print(f"DEBUG: Template data - provinces: {len(provinces)}, districts: {len(districts)}, sub_districts: {len(sub_districts)}, hospital_types: {len(hospital_types)}")
        print(f"DEBUG: First province: {provinces[0] if provinces else 'None'}")
        print(f"DEBUG: First district: {districts[0] if districts else 'None'}")
        print(f"DEBUG: First sub_district: {sub_districts[0] if sub_districts else 'None'}")
        print(f"DEBUG: is_active filter: {status}")
        
        return templates.TemplateResponse("admin/master_data/list.html", {
            "request": request,
            "user": user,
            "page_title": f"{MASTER_DATA_TYPES[data_type]['title']} Management",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "records": records_data,
            "total": total_count,
            "total_count": total_count,  # Add this for pagination template compatibility
            "page": actual_page,
            "limit": limit,
            "search": search,
            "province_code": province_code,
            "district_code": district_code,
            "sub_district_code": sub_district_code,
            "is_active": status,
            "date_from": date_from,
            "date_to": date_to,
            "provinces": provinces,
            "districts": districts,
            "sub_districts": sub_districts,
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
            "total_count": 0,  # Add this for pagination template compatibility
            "page": actual_page,
            "limit": limit,
            "error": f"Failed to load data: {e.detail}",
            "provinces": [],
            "districts": [],
            "sub_districts": [],
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
    if not isinstance(token, str):
        return token
    
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
    if not isinstance(token, str):
        return token
    
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
        
        # For hospitals, get raw document data for enhanced editing
        raw_document_data = {}
        if data_type == "hospitals":
            try:
                # Get raw document for this hospital using its ID
                hospital_id = str(record.get("_id", record.get("id", "")))
                if hospital_id:
                    raw_response = await stardust_api.get_hospitals_raw_documents(
                        token, skip=0, limit=1, hospital_id=hospital_id, include_deleted=True
                    )
                    
                    if raw_response.get("success") and raw_response.get("data", {}).get("raw_documents"):
                        raw_documents = raw_response["data"]["raw_documents"]
                        if raw_documents:
                            raw_document_data = {
                                "raw_document": raw_documents[0],
                                "field_analysis": raw_response["data"].get("field_analysis", {}),
                                "metadata": raw_response["data"].get("metadata", {})
                            }
            except Exception as e:
                print(f"Error loading raw document for hospital edit: {e}")
                pass
        
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
            "hospital_types": hospital_types,
            "raw_document_data": raw_document_data
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
    if not isinstance(token, str):
        return token
    
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
                district_code = record.get("district_code")
                if district_code:
                    # Use the new helper method to find district by code
                    district = await stardust_api.find_district_by_code(token, str(district_code))
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
                            # Use the new helper method to find district by code
                            district = await stardust_api.find_district_by_code(token, str(sub_district.get("district_code")))
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
                district_code = record.get("district_code")
                if not related_data.get("district") and district_code:
                    # Use the new helper method to find district by code
                    district = await stardust_api.find_district_by_code(token, str(district_code))
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
        
        # For hospitals, get raw document data for enhanced details
        raw_document_data = {}
        if data_type == "hospitals":
            try:
                # Get raw document for this hospital using its ID
                hospital_id = str(record.get("_id", record.get("id", "")))
                if hospital_id:
                    raw_response = await stardust_api.get_hospitals_raw_documents(
                        token, skip=0, limit=1, hospital_id=hospital_id, include_deleted=True
                    )
                    
                    if raw_response.get("success") and raw_response.get("data", {}).get("raw_documents"):
                        raw_documents = raw_response["data"]["raw_documents"]
                        if raw_documents:
                            raw_document_data = {
                                "raw_document": raw_documents[0],
                                "field_analysis": raw_response["data"].get("field_analysis", {}),
                                "metadata": raw_response["data"].get("metadata", {})
                            }
            except Exception as e:
                print(f"Error loading raw document for hospital: {e}")
                pass
        
        return templates.TemplateResponse("admin/master_data/detail.html", {
            "request": request,
            "user": user,
            "page_title": f"{MASTER_DATA_TYPES[data_type]['singular']} Detail",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "record": record,
            "related_data": related_data,
            "raw_document_data": raw_document_data,
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
    if not isinstance(token, str):
        return token
    
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
    if not isinstance(token, str):
        return token
    
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
    if not isinstance(token, str):
        return token
    
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
    user, token = await _check_auth_api(request)
    
    try:
        provinces_response = await stardust_api.get_provinces(token, 0, 1000)
        # The dropdown API returns the data directly in the 'data' field
        provinces_data = provinces_response.get("data", {}).get("provinces", [])
        return JSONResponse({"data": provinces_data})
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)

@router.get("/api/master-data/districts/{province_code}")
async def get_districts_by_province(request: Request, province_code: int):
    """Get districts by province code (AJAX endpoint)"""
    user, token = await _check_auth_api(request)
    
    try:
        districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code)
        districts_data = districts_response.get("data", {}).get("districts", [])
        return JSONResponse({"data": districts_data})
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)

@router.get("/api/master-data/sub-districts/{district_code}")
async def get_sub_districts_by_district(request: Request, district_code: int, province_code: Optional[int] = Query(None)):
    """Get sub-districts by district code (AJAX endpoint)"""
    user, token = await _check_auth_api(request)
    
    try:
        # Check if province_code is provided - if not, return error
        if province_code is None:
            return JSONResponse({"error": "province_code is required"}, status_code=400)
        
        sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000, None, province_code, district_code)
        sub_districts_data = sub_districts_response.get("data", {}).get("sub_districts", [])
        return JSONResponse({"data": sub_districts_data})
    except HTTPException as e:
        return JSONResponse({"error": str(e.detail)}, status_code=e.status_code)

@router.post("/admin/master-data/hospitals/{record_id}/update-location")
async def update_hospital_location(request: Request, record_id: str):
    """Update hospital location and address from Google Maps"""
    user, token = await _check_auth_api(request)
    
    try:
        # Get the request data
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

# Additional admin master data endpoints to match Stardust API
@router.get("/admin/dropdown/provinces")
async def admin_get_provinces_dropdown(
    request: Request,
    include_inactive: bool = Query(False, description="Include inactive provinces"),
    include_deleted: bool = Query(False, description="Include soft-deleted provinces"), 
    search: Optional[str] = Query(None, description="Search text across province names"),
    limit: Optional[int] = Query(None, description="Maximum number of results"),
    sort_by: str = Query("en_name", description="Sort field: 'en_name' or 'code'")
):
    """Admin provinces dropdown endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        # Build query parameters for Stardust API
        params = {
            "limit": limit or 1000,
            "skip": 0,
            "search": search,
            "include_inactive": include_inactive,
            "include_deleted": include_deleted,
            "sort_by": sort_by
        }
        
        result = await stardust_api.get_master_data(token, "provinces", **{k: v for k, v in params.items() if v is not None})
        provinces = result.get("data", {}).get("data", [])
        
        return {
            "success": True,
            "data": {
                "provinces": provinces,
                "total": len(provinces),
                "filters_applied": {
                    "include_inactive": include_inactive,
                    "include_deleted": include_deleted,
                    "search": search
                }
            },
            "request_id": "dropdown-provinces",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch provinces: {str(e)}")

@router.get("/admin/dropdown/districts")
async def admin_get_districts_dropdown(
    request: Request,
    province_code: int = Query(..., description="Province code to filter districts"),
    include_inactive: bool = Query(False, description="Include inactive districts"),
    include_deleted: bool = Query(False, description="Include soft-deleted districts"),
    search: Optional[str] = Query(None, description="Search text across district names"),
    limit: Optional[int] = Query(None, description="Maximum number of results"),
    sort_by: str = Query("en_name", description="Sort field: 'en_name' or 'code'")
):
    """Admin districts dropdown endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        params = {
            "limit": limit or 1000,
            "skip": 0, 
            "search": search,
            "province_code": province_code,
            "include_inactive": include_inactive,
            "include_deleted": include_deleted,
            "sort_by": sort_by
        }
        
        result = await stardust_api.get_master_data(token, "districts", **{k: v for k, v in params.items() if v is not None})
        districts = result.get("data", {}).get("data", [])
        
        return {
            "success": True,
            "data": {
                "districts": districts,
                "total": len(districts),
                "province_code": province_code,
                "filters_applied": {
                    "include_inactive": include_inactive,
                    "include_deleted": include_deleted,
                    "search": search
                }
            },
            "request_id": "dropdown-districts",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch districts: {str(e)}")

@router.get("/admin/dropdown/sub-districts")
async def admin_get_sub_districts_dropdown(
    request: Request,
    province_code: int = Query(..., description="Province code to filter sub-districts"),
    district_code: int = Query(..., description="District code to filter sub-districts")
):
    """Admin sub-districts dropdown endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        params = {
            "limit": 1000,
            "skip": 0,
            "province_code": str(province_code),
            "district_code": str(district_code)
        }
        
        result = await stardust_api.get_master_data(token, "sub_districts", **{k: v for k, v in params.items() if v is not None})
        sub_districts = result.get("data", {}).get("data", [])
        
        return {
            "success": True,
            "data": {
                "sub_districts": sub_districts,
                "total": len(sub_districts),
                "province_code": province_code,
                "district_code": district_code
            },
            "request_id": "dropdown-sub-districts", 
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sub-districts: {str(e)}")

# Full CRUD admin master data endpoints
@router.post("/admin/master-data")
async def admin_create_master_data(
    request: Request,
    master_data: MasterDataCreate
):
    """Admin create master data endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.create_master_data(token, master_data.dict())
        return {
            "success": True,
            "message": "Master data record created successfully",
            "data": result.get("data"),
            "request_id": "master-data-create",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create master data: {str(e)}")

@router.get("/admin/master-data/{data_type}")
async def admin_get_master_data(
    request: Request,
    data_type: str,
    limit: int = Query(100, description="Number of records to return", ge=1, le=1000),
    skip: int = Query(0, description="Number of records to skip", ge=0),
    search: Optional[str] = Query(None, description="Search text across data fields"),
    province_code: Optional[int] = Query(None, description="Filter by province code"),
    district_code: Optional[int] = Query(None, description="Filter by district code"),
    sub_district_code: Optional[int] = Query(None, description="Filter by sub-district code")
):
    """Admin get master data endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        params = {
            "limit": limit,
            "skip": skip,
            "search": search,
            "province_code": province_code,
            "district_code": district_code,
            "sub_district_code": sub_district_code
        }
        
        result = await stardust_api.get_master_data(token, data_type, **{k: v for k, v in params.items() if v is not None})
        
        return {
            "success": True,
            "message": "Master data retrieved successfully",
            "data": result.get("data"),
            "request_id": f"admin-master-data-{data_type}",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch master data: {str(e)}")

@router.get("/admin/master-data/{data_type}/{record_id}")
async def admin_get_master_data_record(
    request: Request,
    data_type: str,
    record_id: str
):
    """Admin get specific master data record endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.get_master_data_record(token, data_type, record_id)
        return {
            "success": True,
            "message": "Master data record retrieved successfully",
            "data": result.get("data"),
            "request_id": f"admin-master-data-{data_type}-{record_id}",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch master data record: {str(e)}")

@router.put("/admin/master-data/{data_type}/{record_id}")
async def admin_update_master_data_record(
    request: Request,
    data_type: str, 
    record_id: str,
    master_data: MasterDataUpdate
):
    """Admin update master data record endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.update_master_data(token, data_type, record_id, master_data.dict())
        return {
            "success": True,
            "message": "Master data record updated successfully",
            "data": result.get("data"),
            "request_id": f"admin-master-data-update-{data_type}-{record_id}",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update master data record: {str(e)}")

@router.patch("/admin/master-data/{data_type}/{record_id}")
async def admin_patch_master_data_record(
    request: Request,
    data_type: str,
    record_id: str,
    master_data: MasterDataUpdate
):
    """Admin partially update master data record endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.update_master_data(token, data_type, record_id, master_data.dict())
        return {
            "success": True,
            "message": "Master data record partially updated successfully",
            "data": result.get("data"),
            "request_id": f"admin-master-data-patch-{data_type}-{record_id}",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to partially update master data record: {str(e)}")

@router.delete("/admin/master-data/{data_type}/{record_id}")
async def admin_delete_master_data_record(
    request: Request,
    data_type: str,
    record_id: str
):
    """Admin delete master data record endpoint matching Stardust API"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.delete_master_data(token, data_type, record_id)
        return {
            "success": True,
            "message": "Master data record deleted successfully",
            "data": result.get("data"),
            "request_id": f"admin-master-data-delete-{data_type}-{record_id}",
            "timestamp": "2025-01-08T05:42:00.000Z"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete master data record: {str(e)}")

# Raw Documents Endpoints for Enhanced Hospital Data
@router.get("/admin/hospitals-raw-documents")
async def get_hospitals_raw_documents(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(5, ge=1, le=50, description="Number of documents to return"),
    hospital_id: Optional[str] = Query(None, description="Filter by specific hospital ID"),
    include_deleted: bool = Query(False, description="Include soft-deleted hospitals"),
    province_code: Optional[int] = Query(None, description="Filter by province code"),
    district_code: Optional[int] = Query(None, description="Filter by district code"),
    sub_district_code: Optional[int] = Query(None, description="Filter by sub-district code")
):
    """Get raw hospital documents from MongoDB for detailed analysis"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.get_hospitals_raw_documents(
            token, skip, limit, hospital_id, include_deleted, 
            province_code, district_code, sub_district_code
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch raw hospital documents: {str(e)}")

@router.get("/admin/hospitals/{hospital_id}/raw-document")
async def get_hospital_raw_document(
    request: Request,
    hospital_id: str
):
    """Get raw document for a specific hospital"""
    user, token = await _check_auth_api(request)
    
    try:
        result = await stardust_api.get_hospitals_raw_documents(
            token, skip=0, limit=1, hospital_id=hospital_id, include_deleted=True
        )
        
        if result.get("success") and result.get("data", {}).get("raw_documents"):
            raw_documents = result["data"]["raw_documents"]
            if raw_documents:
                return {
                    "success": True,
                    "message": "Hospital raw document retrieved successfully",
                    "data": {
                        "raw_document": raw_documents[0],
                        "field_analysis": result["data"].get("field_analysis", {}),
                        "metadata": result["data"].get("metadata", {})
                    }
                }
        
        raise HTTPException(status_code=404, detail="Hospital not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hospital raw document: {str(e)}")
