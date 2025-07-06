"""
Qube-Vital device routes for Opera Panel
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.models.auth import User
from app.services.auth import get_current_user_optional
from app.services.stardust_api import stardust_api

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def qube_vital_list(request: Request):
    """Qube-Vital devices list page"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login")
    
    try:
        # Fetch Qube-Vital devices from Stardust API
        devices_data = await stardust_api.get_qube_vital_devices(token)
        
        return templates.TemplateResponse("devices/qube_vital.html", {
            "request": request,
            "user": user,
            "devices": devices_data.get("items", []),
            "page_title": "Qube-Vital Devices"
        })
    except HTTPException as e:
        return templates.TemplateResponse("devices/qube_vital.html", {
            "request": request,
            "user": user,
            "devices": [],
            "error": f"Failed to load Qube-Vital devices: {e.detail}",
            "page_title": "Qube-Vital Devices"
        })

@router.get("/{device_id}", response_class=HTMLResponse)
async def qube_vital_detail(request: Request, device_id: str):
    """Qube-Vital device detail page"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    
    user = await get_current_user_optional(request)
    if not user:
        return RedirectResponse(url="/login")
    
    try:
        # Fetch specific Qube-Vital device from Stardust API
        device_data = await stardust_api.get_qube_vital_device(token, device_id)
        
        return templates.TemplateResponse("devices/qube_vital_detail.html", {
            "request": request,
            "user": user,
            "device": device_data,
            "device_id": device_id,
            "page_title": f"Qube-Vital Device {device_id}"
        })
    except HTTPException as e:
        return templates.TemplateResponse("devices/qube_vital_detail.html", {
            "request": request,
            "user": user,
            "device": {},
            "error": f"Failed to load device: {e.detail}",
            "device_id": device_id,
            "page_title": f"Qube-Vital Device {device_id}"
        })
