"""
AVA4 device routes for Opera Panel
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.auth import User
from app.services.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def ava4_list(request: Request, current_user: User = Depends(get_current_user)):
    """AVA4 devices list page"""
    return templates.TemplateResponse("devices/ava4.html", {
        "request": request,
        "user": current_user,
        "page_title": "AVA4 Devices"
    })

@router.get("/{device_id}", response_class=HTMLResponse)
async def ava4_detail(request: Request, device_id: str, current_user: User = Depends(get_current_user)):
    """AVA4 device detail page"""
    return templates.TemplateResponse("devices/ava4_detail.html", {
        "request": request,
        "user": current_user,
        "device_id": device_id,
        "page_title": f"AVA4 Device {device_id}"
    })
