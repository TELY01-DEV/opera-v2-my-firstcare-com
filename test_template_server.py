#!/usr/bin/env python3
"""
Minimal test server to test templates with mock data
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Import the filter from the master_data routes
def get_localized_name(name_data, language):
    """Extract localized name from name field."""
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

# Mock data
mock_data_config = {
    "title": "Provinces",
    "title_th": "จังหวัด",
    "singular": "Province",
    "singular_th": "จังหวัด",
    "icon": "map-pin"
}

mock_records = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "code": "10",
        "name": [
            {"code": "th", "name": "กรุงเทพมหานคร"},
            {"code": "en", "name": "Bangkok"}
        ],
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002", 
        "code": "11",
        "name": [
            {"code": "th", "name": "สมุทรปราการ"},
            {"code": "en", "name": "Samut Prakan"}
        ],
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "code": "12", 
        "name": [
            {"code": "th", "name": "นนทบุรี"},
            {"code": "en", "name": "Nonthaburi"}
        ],
        "created_at": "2024-01-15T10:30:00Z"
    }
]

mock_user = {
    "username": "testuser",
    "email": "test@example.com",
    "role": "admin"
}

@app.get("/test-template", response_class=HTMLResponse)
async def test_template(request: Request, lang: str = "th"):
    """Test the master data template with mock data"""
    return templates.TemplateResponse("admin/master_data/list.html", {
        "request": request,
        "user": mock_user,
        "page_title": "Provinces Management",
        "data_type": "provinces",
        "data_config": mock_data_config,
        "records": mock_records,
        "total": len(mock_records),
        "page": 1,
        "limit": 20,
        "search": None,
        "province_code": None,
        "district_code": None,
        "provinces": [],
        "districts": [],
        "hospital_types": [],
        "language": lang
    })

@app.get("/")
async def root():
    return {"message": "Template test server"}

if __name__ == "__main__":
    print("🧪 Starting template test server...")
    print("📝 Test URL: http://localhost:8001/test-template")
    print("🌏 Thai version: http://localhost:8001/test-template?lang=th")
    print("🌍 English version: http://localhost:8001/test-template?lang=en")
    uvicorn.run(app, host="127.0.0.1", port=8001)
