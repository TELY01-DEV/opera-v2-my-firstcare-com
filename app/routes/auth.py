"""
Authentication routes for Opera Panel
"""
from fastapi import APIRouter, Request, HTTPException, status, Form, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.models.auth import LoginRequest
from app.services.auth import auth_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/login")
async def login(request: Request, login_data: LoginRequest):
    """Handle login JSON submission"""
    try:
        print(f"DEBUG: Login attempt for user: {login_data.username}")
        token = await auth_service.login(login_data)
        print(f"DEBUG: Successfully got token from Stardust: {token.access_token[:20]}...")
        print(f"DEBUG: Refresh token: {token.refresh_token[:20] if token.refresh_token else 'None'}...")
        
        # Store tokens in session
        request.session["access_token"] = token.access_token
        if token.refresh_token:
            request.session["refresh_token"] = token.refresh_token
        print(f"DEBUG: Tokens stored in session")
        print(f"DEBUG: Session after storing tokens: {dict(request.session)}")
        
        return JSONResponse(
            content={"success": True, "message": "Login successful"},
            status_code=200
        )
    
    except HTTPException as e:
        print(f"DEBUG: Login failed: {e.detail}")
        return JSONResponse(
            content={"detail": e.detail},
            status_code=e.status_code
        )

@router.post("/login-form")
async def login_form(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle traditional form-based login submission"""
    try:
        print(f"DEBUG: Form login attempt for user: {username}")
        login_data = LoginRequest(username=username, password=password)
        token = await auth_service.login(login_data)
        print(f"DEBUG: Successfully got token from Stardust: {token.access_token[:20]}...")
        print(f"DEBUG: Refresh token: {token.refresh_token[:20] if token.refresh_token else 'None'}...")
        
        # Store tokens in session
        request.session["access_token"] = token.access_token
        if token.refresh_token:
            request.session["refresh_token"] = token.refresh_token
        print(f"DEBUG: Tokens stored in session")
        
        # Redirect to dashboard
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    except HTTPException as e:
        print(f"DEBUG: Login failed: {e.detail}")
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": e.detail,
            "page_title": "Login"
        })

@router.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/me", response_class=HTMLResponse)
async def get_profile(request: Request):
    """Get current user profile"""
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        profile = await auth_service.get_user_profile(token)
        
        # Language detection and localization
        from app.utils import get_user_language, get_copyright_text, get_mfc_logo
        language = get_user_language(request)
        
        return templates.TemplateResponse("auth/profile.html", {
            "request": request,
            "profile": profile,
            "page_title": "User Profile",
            "language": language,
            "copyright_text": get_copyright_text(language),
            "mfc_logo": get_mfc_logo(language)
        })
    except HTTPException:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/me/json")
async def get_profile_json(request: Request):
    """Get current user profile as JSON"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profile = await auth_service.get_user_profile(token)
    return profile

@router.get("/debug")
async def debug_auth():
    """Debug endpoint to test Stardust-V1 API connection"""
    import os
    return {
        "stardust_auth_url": os.getenv("STARDUST_AUTH_URL", "Not configured"),
        "dev_username": os.getenv("DEV_USERNAME", "Not configured"),
        "status": "Authentication service ready"
    }
