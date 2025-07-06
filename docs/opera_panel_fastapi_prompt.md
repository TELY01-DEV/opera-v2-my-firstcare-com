
# 🚀 My FirstCare Opera Panel — FastAPI + Stardust API Integration

## 🩺 System Migration Overview

This version upgrades the Opera Panel to use **FastAPI Endpoints** from `https://stardust.my-firstcare.com` instead of direct MongoDB queries. All system operations (Patients, Devices, Master Data, Medical History, FHIR Audit Logs) are now accessed via REST API endpoints.

---

## 📦 Project Initialization

### Project Details

| Key                        | Value                                            |
|---------------------------|--------------------------------------------------|
| Project Name              | My FirstCare Opera Panel                         |
| Admin Panel URL           | https://opera.my-firstcare.com                  |
| API Base URL              | https://stardust.my-firstcare.com               |
| Swagger                   | https://stardust.my-firstcare.com/docs          |
| OpenAPI JSON              | https://stardust.my-firstcare.com/openapi.json  |
| API Port                  | `5055`                                           |
| Auth Server               | https://stardust-v1.my-firstcare.com            |
| Authentication            | JWT-based, RBAC (superadmin, operator, viewer)  |

---

## 📁 Directory Structure

```bash
/app
  /routes
    ava4.py
    kati.py
    qube_vital.py
    admin.py
    auth.py
  /models
    ava4.py
    kati.py
    qube_vital.py
    audit_log.py
  /templates     # Jinja2 + Tabler.io UI
  /services
    auth.py
    audit_logger.py
  /static
main.py
.env
requirements.txt
Dockerfile
docker-compose.yml
```

---

## 🧪 Getting Started

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run local dev
uvicorn main:app --reload --port 5055
```

---

## 🐳 Docker Deployment

```bash
docker-compose up -d
docker-compose -f docker-compose.logging.yml up -d  # Optional logging stack
```

---

## 🔒 Auth & JWT

- Use `/auth/login` from Stardust-V1 to get `access_token`
- Pass token via `Authorization: Bearer <token>` to all protected routes
- Use `/auth/me` to get user profile, photo, phone, etc.
- Refresh tokens if expired

---

## 🧩 Admin Panel Features

- ✅ Patient List + Profile CRUD  
- ✅ AVA4, Kati, Qube-Vital Device CRUD  
- ✅ Device Assignment & Status  
- ✅ Vital Sign Logs + Chart Visualization  
- ✅ Hospital + Geo Master Data (province, district, sub-district)  
- ✅ Audit Log View (FHIR Provenance)  
- ✅ JWT Login / Profile Avatar / User Info  
- ✅ Settings Page  
- ✅ Real-time Update (Socket.IO)

---

## 📈 Dashboard Analytics API

Suggested Endpoints:

```http
GET /stats/patient-count
GET /stats/device-usage
GET /stats/vital-trends?patient_id=...
GET /stats/alerts?type=SPO2_low&since=30d
```

Use Tabler + Chart.js on frontend.

---

## 🛡️ FHIR R5 Audit Log (Provenance Resource)

FHIR Provenance creation from Observation:

```json
{
  "recorded": "2025-07-06T15:30:00Z",
  "agent": [{
    "who": {
      "identifier": { "value": "KATI-123456789" }
    },
    "type": {
      "text": "device"
    }
  }],
  "entity": [{
    "what": {
      "identifier": { "value": "WEIGHT" }
    }
  }],
  "target": [{
    "reference": "Observation/OBS-ID-001",
    "type": "Observation"
  }]
}
```

---

## 🧩 Device Mapping

| Device        | Field        | Maps To       |
|---------------|--------------|----------------|
| AVA4          | mac_address  | patients.ava_mac_address |
| Kati Watch    | imei         | patients.watch_mac_address |
| Qube-Vital    | imei         | hospitals.mac_hv01_box |

---

## 🧩 Soft Delete Example

```json
{
  "deleted": false,
  "deleted_at": null,
  "deleted_by": null
}
```

---

## ✅ Summary

- MongoDB now used **only for internal services** — all user-facing data via API
- Secure, scalable, and easier to audit
- Compatible with FHIR + JWT + Tabler stack
- Real-time and analytics-ready for future AI agent expansion
