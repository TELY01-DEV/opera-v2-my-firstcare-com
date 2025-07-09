"""
Admin routes for Opera Panel
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.models.auth import User
from app.services.auth import get_current_user_optional
from app.services.stardust_api import stardust_api

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/patients", response_class=HTMLResponse)
async def patients_list(request: Request):
    """Patients management page"""
    # Check authentication via session
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login")
    
    try:
        # Fetch patients from Stardust API
        patients_data = await stardust_api.get_patients(token)
        
        return templates.TemplateResponse("admin/patients.html", {
            "request": request,
            "user": user,
            "patients": patients_data.get("items", []),
            "page_title": "Patient Management"
        })
    except HTTPException as e:
        return templates.TemplateResponse("admin/patients.html", {
            "request": request,
            "user": user,
            "patients": [],
            "error": f"Failed to load patients: {e.detail}",
            "page_title": "Patient Management"
        })

@router.get("/hospitals", response_class=HTMLResponse)
async def hospitals_list(request: Request):
    """Hospitals management page"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login")
    
    try:
        # Get filter parameters
        province_filter = request.query_params.get("province")
        district_filter = request.query_params.get("district")
        sub_district_filter = request.query_params.get("sub_district")
        type_filter = request.query_params.get("type")
        search_filter = request.query_params.get("search")
        
        # Fetch hospitals from Stardust API
        hospitals_data = await stardust_api.get_hospitals(token)
        hospitals = hospitals_data.get("items", [])
        
        # Apply filters
        if province_filter:
            hospitals = [h for h in hospitals if h.get("province_code") == province_filter]
        if district_filter:
            hospitals = [h for h in hospitals if h.get("district_code") == district_filter]
        if sub_district_filter:
            hospitals = [h for h in hospitals if h.get("sub_district_code") == sub_district_filter]
        if type_filter:
            hospitals = [h for h in hospitals if h.get("hospital_type") == type_filter]
        if search_filter:
            search_lower = search_filter.lower()
            hospitals = [h for h in hospitals if 
                        search_lower in (h.get("name", "") or "").lower() or
                        search_lower in (h.get("address", "") or "").lower() or
                        search_lower in (h.get("province", "") or "").lower() or
                        search_lower in (h.get("district", "") or "").lower()]
        
        # Fetch provinces for the filter dropdown
        try:
            provinces_data = await stardust_api.get_provinces(token, 0, 1000)
            provinces = provinces_data.get("data", {}).get("provinces", [])
            print(f"DEBUG: Fetched {len(provinces)} provinces")
        except Exception as e:
            print(f"DEBUG: Error fetching provinces: {e}")
            provinces = []
        
        return templates.TemplateResponse("admin/hospitals.html", {
            "request": request,
            "user": user,
            "hospitals": hospitals,
            "provinces": provinces,
            "page_title": "Hospital Management"
        })
    except HTTPException as e:
        return templates.TemplateResponse("admin/hospitals.html", {
            "request": request,
            "user": user,
            "hospitals": [],
            "provinces": [],
            "error": f"Failed to load hospitals: {e.detail}",
            "page_title": "Hospital Management"
        })

@router.get("/audit-logs", response_class=HTMLResponse)
async def audit_logs(request: Request):
    """Audit logs page"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login")
    
    try:
        # Fetch audit logs from Stardust API
        logs_data = await stardust_api.get_audit_logs(token)
        
        return templates.TemplateResponse("admin/audit_logs.html", {
            "request": request,
            "user": user,
            "logs": logs_data.get("items", []),
            "page_title": "Audit Logs"
        })
    except HTTPException as e:
        return templates.TemplateResponse("admin/audit_logs.html", {
            "request": request,
            "user": user,
            "logs": [],
            "error": f"Failed to load audit logs: {e.detail}",
            "page_title": "Audit Logs"
        })

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    """Settings page"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "user": user,
        "page_title": "Settings"
    })
