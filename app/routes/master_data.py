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
        # Fetch data from Stardust API
        data_response = await stardust_api.get_master_data(
            token, data_type, skip, limit, search, province_code_int, district_code_int,
            is_active_bool, date_from, date_to
        )
        
        # Get reference data for dropdowns
        provinces = []
        districts = []
        hospital_types = []
        
        if data_type in ["districts", "sub-districts", "hospitals"]:
            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
            provinces = provinces_response.get("data", [])
        
        # Load districts for sub-districts and hospitals pages
        if data_type in ["sub-districts", "hospitals"]:
            if province_code_int:
                # Load districts filtered by province for the dropdown filter
                districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code_int)
            else:
                # Load all districts for displaying district names in the table
                districts_response = await stardust_api.get_districts(token, 0, 1000, None)
            districts = districts_response.get("data", [])
            
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            hospital_types = hospital_types_response.get("data", [])
        
        return templates.TemplateResponse("admin/master_data/list.html", {
            "request": request,
            "user": user,
            "page_title": f"{MASTER_DATA_TYPES[data_type]['title']} Management",
            "data_type": data_type,
            "data_config": MASTER_DATA_TYPES[data_type],
            "records": data_response.get("data", []),
            "total": data_response.get("total", 0),
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
            provinces = provinces_response.get("data", [])
        
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            hospital_types = hospital_types_response.get("data", [])
        
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
        record = await stardust_api.get_master_data_record(token, data_type, record_id)
        
        # Get reference data for dropdowns
        provinces = []
        districts = []
        hospital_types = []
        
        if data_type in ["districts", "sub-districts", "hospitals"]:
            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
            provinces = provinces_response.get("data", [])
        
        if data_type in ["sub-districts", "hospitals"] and record.get("province_code"):
            districts_response = await stardust_api.get_districts(token, 0, 1000, None, record.get("province_code"))
            districts = districts_response.get("data", [])
            
        if data_type == "hospitals":
            hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
            hospital_types = hospital_types_response.get("data", [])
        
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
    
    token = auth_result
    
    try:
        # Get the record
        record = await stardust_api.get_master_data_record(token, data_type, record_id)
        
        # Get related data for context display
        related_data = {}
        
        # For districts, get province info
        if data_type == "districts" and record.get("province_code"):
            try:
                provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                provinces = provinces_response.get("data", [])
                province = next((p for p in provinces if p.get("code") == record.get("province_code")), None)
                if province:
                    related_data["province"] = province
            except:
                pass
        
        # For sub-districts, get district and province info
        if data_type == "sub-districts":
            try:
                if record.get("district_code"):
                    districts_response = await stardust_api.get_districts(token, 0, 1000)
                    districts = districts_response.get("data", [])
                    district = next((d for d in districts if d.get("code") == record.get("district_code")), None)
                    if district:
                        related_data["district"] = district
                        
                        if district.get("province_code"):
                            provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                            provinces = provinces_response.get("data", [])
                            province = next((p for p in provinces if p.get("code") == district.get("province_code")), None)
                            if province:
                                related_data["province"] = province
            except:
                pass
        
        # For hospitals, get all location hierarchy and hospital type
        if data_type == "hospitals":
            try:
                if record.get("hospital_type_code"):
                    hospital_types_response = await stardust_api.get_hospital_types(token, 0, 1000)
                    hospital_types = hospital_types_response.get("data", [])
                    hospital_type = next((ht for ht in hospital_types if ht.get("code") == record.get("hospital_type_code")), None)
                    if hospital_type:
                        related_data["hospital_type"] = hospital_type
                
                # Get location hierarchy
                if record.get("sub_district_code"):
                    sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000)
                    sub_districts = sub_districts_response.get("data", [])
                    sub_district = next((sd for sd in sub_districts if sd.get("code") == record.get("sub_district_code")), None)
                    if sub_district:
                        related_data["sub_district"] = sub_district
                        
                        if sub_district.get("district_code"):
                            districts_response = await stardust_api.get_districts(token, 0, 1000)
                            districts = districts_response.get("data", [])
                            district = next((d for d in districts if d.get("code") == sub_district.get("district_code")), None)
                            if district:
                                related_data["district"] = district
                                
                                if district.get("province_code"):
                                    provinces_response = await stardust_api.get_provinces(token, 0, 1000)
                                    provinces = provinces_response.get("data", [])
                                    province = next((p for p in provinces if p.get("code") == district.get("province_code")), None)
                                    if province:
                                        related_data["province"] = province
            except:
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
@router.get("/api/master-data/districts/{province_code}")
async def get_districts_by_province(request: Request, province_code: int):
    """Get districts by province code (AJAX endpoint)"""
    user, auth_result = await _check_auth(request)
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    token = auth_result
    
    try:
        districts_response = await stardust_api.get_districts(token, 0, 1000, None, province_code)
        return JSONResponse({"success": True, "data": districts_response.get("data", [])})
    except HTTPException as e:
        return JSONResponse({"success": False, "error": str(e.detail)}, status_code=e.status_code)

@router.get("/api/master-data/sub-districts/{district_code}")
async def get_sub_districts_by_district(request: Request, district_code: int):
    """Get sub-districts by district code (AJAX endpoint)"""
    user, auth_result = await _check_auth(request)
    if not user:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    
    token = auth_result
    
    try:
        sub_districts_response = await stardust_api.get_sub_districts(token, 0, 1000, None, None, district_code)
        return JSONResponse({"success": True, "data": sub_districts_response.get("data", [])})
    except HTTPException as e:
        return JSONResponse({"success": False, "error": str(e.detail)}, status_code=e.status_code)
