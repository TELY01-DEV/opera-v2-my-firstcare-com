# 🚀 My FirstCare Opera Panel

FastAPI-based admin panel for healthcare device management, integrating with Stardust API.

## 🩺 Features

- **Patient Management** - CRUD operations for patient profiles
- **Device Management** - AVA4, Kati Watch, Qube-Vital device monitoring
- **Real-time Dashboard** - Vital signs, alerts, and device status
- **JWT Authentication** - Secure login with role-based access control
- **FHIR Compliance** - Audit logs using FHIR R5 Provenance
- **Modern UI** - Tabler.io with responsive design

## 🏗️ Architecture

```
Opera Panel (FastAPI) → Stardust API → Database
                     ↗ Stardust-V1 (Auth)
```

- **Opera Panel**: Frontend admin interface (this project)
- **Stardust API**: Backend API for all data operations
- **Stardust-V1**: Authentication service

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd opera-v2-my-firstcare-com
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload --port 5055
   ```

6. **Access the panel**
   - Open: http://localhost:5055
   - Login with your Stardust-V1 credentials

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📁 Project Structure

```
/app
  /routes          # FastAPI route handlers
    auth.py        # Authentication routes
    admin.py       # Admin panel routes
    ava4.py        # AVA4 device routes
    kati.py        # Kati device routes
    qube_vital.py  # Qube-Vital device routes
  /models          # Pydantic models
    auth.py        # User/auth models
    ava4.py        # AVA4 device models
  /services        # Business logic
    auth.py        # Authentication service
  /templates       # Jinja2 templates
    base.html      # Base template
    dashboard.html # Main dashboard
    /auth          # Auth templates
    /admin         # Admin templates
    /devices       # Device templates
  /static          # CSS, JS, images
main.py            # FastAPI app entry point
requirements.txt   # Python dependencies
Dockerfile         # Container definition
docker-compose.yml # Multi-container setup
```

## 🔒 Authentication

The panel uses JWT-based authentication through Stardust-V1:

1. User enters credentials in login form
2. Panel sends credentials to Stardust-V1 `/auth/login`
3. Stardust-V1 returns JWT access token
4. Panel stores token in session
5. All API calls include `Authorization: Bearer <token>`

### Roles

- **superadmin**: Full access to all features
- **operator**: Can manage patients and devices
- **viewer**: Read-only access

## 🌐 API Integration

All data operations go through the Stardust API:

### Endpoints Used

```http
# Authentication (Stardust-V1)
POST /auth/login
GET  /auth/me

# Patients (Stardust API)
GET    /patients
POST   /patients
GET    /patients/{id}
PUT    /patients/{id}
DELETE /patients/{id}

# Devices (Stardust API)
GET    /devices/ava4
GET    /devices/kati
GET    /devices/qube-vital

# Analytics (Stardust API)
GET    /stats/patient-count
GET    /stats/device-usage
GET    /stats/vital-trends
```

## 🎨 UI Components

Built with **Tabler.io** framework:
- Responsive design
- Modern dashboard widgets
- Chart.js integration
- Real-time updates
- Mobile-friendly

## 🔧 Configuration

Environment variables in `.env`:

```bash
# API Configuration
STARDUST_API_BASE_URL=https://stardust.my-firstcare.com
STARDUST_AUTH_URL=https://stardust-v1.my-firstcare.com

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Panel Settings
PANEL_HOST=0.0.0.0
PANEL_PORT=5055
DEBUG=True
```

## 🏥 Device Types

### AVA4
- Multi-parameter vital signs monitor
- Tracks: Heart rate, Blood pressure, SpO2, Temperature
- Maps to: `patients.ava_mac_address`

### Kati Watch
- Wearable health device
- Tracks: Steps, Heart rate, Sleep
- Maps to: `patients.watch_mac_address`

### Qube-Vital
- Hospital-grade monitoring box
- Tracks: Environmental data, Patient proximity
- Maps to: `hospitals.mac_hv01_box`

## 📊 Dashboard Features

- **Real-time Stats**: Patient count, device status, vital signs
- **Charts**: Vital sign trends, device distribution
- **Alerts**: Critical health alerts and device issues
- **Activity Feed**: Recent patient and device activities

## 🛡️ FHIR Compliance

Audit logs use FHIR R5 Provenance resources:

```json
{
  "resourceType": "Provenance",
  "recorded": "2025-07-06T15:30:00Z",
  "agent": [{
    "who": {"identifier": {"value": "KATI-123456789"}},
    "type": {"text": "device"}
  }],
  "target": [{
    "reference": "Observation/OBS-ID-001",
    "type": "Observation"
  }]
}
```

## 🚀 Deployment

### Production Considerations

1. **Security**
   - Change `SECRET_KEY` in production
   - Use HTTPS only
   - Enable CORS restrictions
   - Implement rate limiting

2. **Performance**
   - Use Redis for session storage
   - Enable caching for API responses
   - Configure load balancing

3. **Monitoring**
   - Health checks enabled
   - Log aggregation
   - Performance monitoring

### Docker Production

```bash
# Production compose
docker-compose -f docker-compose.prod.yml up -d

# With logging stack
docker-compose -f docker-compose.logging.yml up -d
```

## 🔧 Development

### Adding New Features

1. **New Route**: Add to `/app/routes/`
2. **New Model**: Add to `/app/models/`
3. **New Template**: Add to `/app/templates/`
4. **Update Navigation**: Edit `base.html`

### API Service Pattern

```python
# app/services/patient_service.py
class PatientService:
    async def get_patients(self, token: str):
        response = await self.client.get(
            f"{STARDUST_API_URL}/patients",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## 📞 Support

- **Documentation**: Check `/docs` endpoints
- **API Reference**: https://stardust.my-firstcare.com/docs
- **Issues**: Create GitHub issues for bugs

## 📄 License

Licensed under the MIT License. See `LICENSE` file for details.

---

**My FirstCare Opera Panel v2.0** - Healthcare Administration Made Simple
