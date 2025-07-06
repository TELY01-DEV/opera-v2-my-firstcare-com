"""
My FirstCare Opera Panel - FastAPI + Stardust API Integration
Main application entry point
"""
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os

from app.routes import auth, admin, ava4, kati, qube_vital, api
from app.services.auth import get_current_user
from app.models.auth import User

app = FastAPI(
    title="My FirstCare Opera Panel",
    description="Healthcare Admin Panel with Stardust API Integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "opera-panel-secret-key-change-in-production"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(ava4.router, prefix="/devices/ava4", tags=["AVA4 Devices"])
app.include_router(kati.router, prefix="/devices/kati", tags=["Kati Devices"])
app.include_router(qube_vital.router, prefix="/devices/qube-vital", tags=["Qube-Vital Devices"])
app.include_router(api.router, prefix="/api", tags=["API"])

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    # Check if user is authenticated via session
    print(f"DEBUG: Session contents: {dict(request.session)}")
    print(f"DEBUG: Session cookies: {request.cookies}")
    token = request.session.get("access_token")
    print(f"DEBUG: Session token exists: {token is not None}")
    if not token:
        print("DEBUG: No token in session, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        from app.services.auth import auth_service
        print(f"DEBUG: Attempting to get user profile with token: {token[:20]}...")
        profile = await auth_service.get_user_profile(token)
        print(f"DEBUG: Successfully got user profile: {profile.username}")
        user = User(
            id=profile.id or profile.username,  # Use username as fallback ID
            username=profile.username,
            email=profile.email,
            full_name=profile.full_name,
            role=profile.role,
            profile_photo=profile.profile_photo,
            phone=profile.phone,
            permissions=profile.permissions or [],
            system_access=profile.system_access
        )
        
        # Language detection and localization
        from app.utils import get_user_language, get_copyright_text, get_mfc_logo
        language = get_user_language(request)
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "page_title": "Dashboard",
            "language": language,
            "copyright_text": get_copyright_text(language),
            "mfc_logo": get_mfc_logo(language)
        })
    except Exception as e:
        print(f"DEBUG: Error getting user profile: {str(e)}")
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "page_title": "Login"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "opera-panel"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5055,
        reload=True
    )
