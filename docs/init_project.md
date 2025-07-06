# My FirstCare Opera Panel - Project Initialization

## Project Overview
This document outlines the initialization and setup of the My FirstCare Opera Panel API system.

## Project Details
- **Project Name**: Opera Panel My FirstCare Platform
- **Framework**: FastAPI
- **Stardust API**: stardust.myfirstcare.com:5054
- **Authentication**: JWT-based
- **Deployment**: Docker containerization

## Directory Structure
`

## Getting Started

### 1. Environment Setup
```bash
# port setting
port:5055
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create environment variables or update the configuration files:
- PHR/Medical Data/Devices/Master Data call via FastAPI at stardust.my-firstcare.com
- JWT secret keys

### 3. Docker Deployment
```bash
# Build and run the main application
docker-compose up -d

# Deploy monitoring stack
docker-compose -f docker-compose.logging.yml up -d
```

### 4. Verify Installation
- **Application**: http://localhost:5055
- **Health Check**: http://localhost:5055/health

## Container Services
- **opera=panel-my-firstcare-com**: Main application
- **opera=panel-elasticsearch**: Log storage
- **opera=panel--kibana**: Log visualization
- **opera=panel--logstash**: Log processing
- **opera=panel--filebeat**: Log shipping

## Initial Configuration Complete
The project has been successfully initialized with comprehensive logging, monitoring, and error handling systems.

# 🚀 My FirstCare Opera Panel: Admin Panel Tabler Template + Stardust Auth + FHIR R5 Audit Log

**Authentication:** ✅ **FULLY OPERATIONAL** - Stardust-V1 validated with admin credentials  
**Core APIs:** Hospital, Patient, Geography endpoints validated  
**Medical History:** All 14 collections validated (6,898 records)  
**Docker Deployment:** Running stable on port 5055  

---

Prompt:

Build a complete backend system using FastAPI and MongoDB to manage medical IoT devices: AVA4, Kati Watch, and Qube-Vital. The system must include:

Project Name: `My FirstCare Opera Panel` (`opera-panel-my-firstcare-com`)
Admin Panel URL: `https://opera.my-firstcare.com`
API Port: `5055`
Stardust API: https://stardust.my-firstcare.com
Swagger Document: https://stardust.my-firstcare.com/docs
OpenAPI JSON: https://stardust.my-firstcare.com/openapi.json
Project implementation to deploy by Docker Service



## 🖥️ 1. Admin Panel (Jinja2 + Tabler)

Build a web admin dashboard with:
- FastAPI + Jinja2 for rendering
- Tabler.io components for UI
- Socket.IO for real-time updates
- JWT authentication via Stardust-V1
- Auth-protected access + RBAC (super admin, operator, viewer)
- Pages:
  - Patient list & profile CRUD 
  - Device list (AVA4, Kati, Qube-Vital)CRUD 
  - Vital Sign logs with charts
  - Device assignment and status
  - Master data management (hospitals, provinces, districts, sub-districts,) CRUD
  - Audit Log for viewing FHIR Provenance resources
  - Settings page for system configuration
- API Swagger documentation for all endpoints stardust.my-firstcare.com/openapi.json
- User Profile management with JWT token refresh display/edit user profile Avatar photo profile for stardust-v1.my-firstcare.com/auth/me (https://stardust-v1.my-firstcare.com/openapi.json)

---

## 🛡️ 4. FHIR R5 Audit Log (Provenance Resource)

check form this: stardust.my-firstcare.com/openapi.json

- Generate a `Provenance` resource based on FHIR R5
- Fields:
  - `recorded`: current timestamp
  - `agent.who.identifier.value`: device ID (mac/imei)
  - `agent.type.text`: "device"
  - `entity.what.identifier.value`: type of observation (e.g. "WEIGHT")
  - `target.reference`: the Observation ID created
- `target.type`: "Observation

---

## 📁 Suggested Project Structure

```
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
  /templates     → Jinja2 + Tabler
  /services
    mongo.py
    auth.py
    audit_logger.py
  /static
main.py
.env
requirements.txt
docker-compose.yml
Dockerfile
```

---

## 📊 Mermaid ER Diagram (updated)

```mermaiderDiagram
  patients ||--o{ watches : uses
  patients ||--o{ amy_boxes : uses
  patients }o--|| hospitals : registered_in
  hospitals ||--o{ mfc_hv01_boxes : owns
  hospitals }o--|| provinces : in
  hospitals }o--|| districts : in
  hospitals }o--|| sub_districts : in
  patients ||--o{ medical_histories : has
  watches ||--o{ medical_histories : sends
  amy_boxes ||--o{ medical_histories : sends
  mfc_hv01_boxes ||--o{ medical_histories : sends
  medical_histories }o--|| fhir_observations : converted_to
  medical_histories }o--|| fhir_provenance : audited_by
```

Hospital Provinces, districts, and sub-districts are linked to hospitals, which in turn link to patients. Each device sends health data that is stored in specific collections.

### **Geographic and Organization Collections:**
| รายการ                  | ไฟล์/Collection                      |
| ----------------------- | ----------------------------------- |
| Hospital (Organization) | `AMY.hospitals`                     |
| Sub-District            | `AMY.sub_districts`                 |
| District                | `AMY.districts`                     |
| Province                | `AMY.provinces`                     |

### **Patient and Device Collections:** ✅ **VALIDATED - ALL COLLECTIONS ACTIVE**
| รายการ                          | ไฟล์/Collection                     | 📊 Status |
| ------------------------------- | ---------------------------------- | --------- |
| Patient                         | `AMY.patients`                     | ✅ **211 patients** |
| AVA4 (Box)                      | `AMY.amy_boxes`                    | ✅ **99 boxes** |
| AVA4 Sub-device                 | `AMY.amy_devices`                  | ✅ **74 devices** |
| Kati Watch                      | `AMY.watches`                      | ✅ **121 watches** |
| Qube-Vital (โรงพยาบาล)          | `AMY.mfc_hv01_boxes`               | ✅ **2 devices** |

### **Medical History Collections:** ✅ **VALIDATED - ALL ACTIVE**
This is collection of medical/health history data from devices, linked to patients and hospitals.

| รายการ                          | Collection                         | 📊 Status |
| ------------------------------- | ---------------------------------- | --------- |
| Blood Pressure History          | `AMY.blood_pressure_histories`     | ✅ **2,243 records** |
| Blood Sugar History             | `AMY.blood_sugar_histories`        | ✅ **13 records** |
| Body Data History               | `AMY.body_data_histories`          | ✅ **15 records** |
| Creatinine History              | `AMY.creatinine_histories`         | ✅ **3 records** |
| Lipid History                   | `AMY.lipid_histories`              | ✅ **4 records** |
| Sleep Data History              | `AMY.sleep_data_histories`         | ✅ **79 records** |
| SPO2 History                    | `AMY.spo2_histories`               | ✅ **1,724 records** |
| Step History                    | `AMY.step_histories`               | ✅ **133 records** |
| Temperature Data History        | `AMY.temprature_data_histories`    | ✅ **2,574 records** |
| **Additional Collections:**     |                                    |           |
| Admit Data History              | `AMY.admit_data_histories`         | ✅ **74 records** |
| Allergy History                 | `AMY.allergy_histories`            | ✅ **11 records** |
| Medication History              | `AMY.medication_histories`         | ✅ **12 records** |
| Underlying Disease History      | `AMY.underlying_disease_histories` | ✅ **13 records** |
| Sleep History (Empty)           | `AMY.sleep_histories`              | ⚠️ **0 records** |

**📊 Medical History Summary:** 14 collections with **6,898 total medical records** - All properly linked to patients with timestamps

---

## **Device-Collection Mapping:**

AVA4, Kati Watch, and Qube-Vital devices send health data to specific collections in MongoDB. The medical history collections are:

| Device                  | Collection                    | Mapping                    |
| ----------------------- | ----------------------------- | -------------------------- |
| AVA4 (Box)              | `AMY.amy_boxes`               | จะ mapping กับ `patients`   |
| AVA4 Sub-device         | `AMY.amy_devices`             | Linked to `amy_boxes`      |
| Kati Watch             | `AMY.watches`         | จะ mapping กับ `patients` ✅ **ENDPOINTS AVAILABLE**  |
| Qube-Vital (โรงพยาบาล) | `AMY.mfc_hv01_boxes`  | Mapping กับ `hospitals`    |

---

## 🧩 ความสัมพันธ์ (Relations)

| Entity                  | Field ใช้เชื่อมโยง                                                      |
| ----------------------- | -------------------------------------------------------------------- |
| Hospital → Province     | `hospital.province_code = province.code`                             |
| Hospital → District     | `hospital.district_code = district.code`                             |
| Hospital → Sub-District | `hospital.sub_district_code = sub_district.code`                     |
| Hospital → Qube-Vital   | `hospital.mac_hv01_box` เท่ากับ Qube-Vital MAC (ใน `mfc_hv01_boxes`)   |

---

## 🧩 Entity Relationship Summary

| Entity                                 | Field                                                      | ความสัมพันธ์                                                 |
| -------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------- |
| **Patient** (`patients`)               | `watch_mac_address`, `ava_mac_address`, `new_hospital_ids` | → Kati Watch, AVA4, Hospital                              |
| **AVA4** (`amy_boxes`)                 | `mac_address`, `patient_id`                                | → เชื่อมด้วย `ava_mac_address` หรือ mapping ใน `patients`     |
| **Kati Watch** (`watches`)             | `imei`, `patient_id`                                       | → เชื่อมกับ `patients._id`                                   |
| **Qube-Vital** (`mfc_hv01_boxes`)      | `imei_of_hv01_box`, `hospital_id`                          | → เชื่อมกับ `hospitals._id`                                  |
| **Hospital** (`hospitals`)             | `province_code`, `district_code`, `sub_district_code`      | → เขตพื้นที่ (ใช้ใน Map + UI filter)                           |
| **Province / District / Sub-district** | `code`                                                     | → ใช้เชื่อมในทุก entity ที่อยู่ในสถานที่                            |

---

## 🧩 My FirstCare Opera Panel: Additional Enhancements

This section extends the system with improvements for TTL, Soft Delete, and preparation for future features.

---

## 📅 TTL / Index on History and Logs

**(✅ Added Above)**

---

## 📋 Soft Delete & Delete Log

Implement soft delete for sensitive collections such as patient, devices, or history.

### Example:

```python
# In each model document
{
  "deleted": false,
  "deleted_at": null,
  "deleted_by": null
}
```

### Behavior:

- `GET` routes must filter by `{ deleted: false }`
- `DELETE` routes update `deleted = true` and log `deleted_by` + `deleted_at`
- Keep delete logs in a dedicated collection `delete_logs` or via FHIR `Provenance`

---

## 📈 Dashboard Analytics API

Build endpoints for:
- `/stats/patient-count`
- `/stats/device-usage`
- `/stats/vital-trends?patient_id=...`
- `/stats/alerts?type=SPO2_low&since=30d`

Backend returns JSON → Frontend renders charts using Chart.js or Tabler widget

---

## 🔄 Webhook

Add a feature where when a new history entry is inserted, trigger a webhook to external system.

```python
def notify_webhook(data):
    requests.post(WEBHOOK_URL, json=data)
```

Use via background task or event queue (e.g. Celery or FastAPI BackgroundTasks)
