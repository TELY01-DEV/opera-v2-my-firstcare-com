
# 📄 .env Configuration for AMY Unified Platform

This file defines environment variables for the FastAPI + MongoDB + Stardust Auth system.

```env
# Environment Configuration
DEBUG=true
PORT=5055

# Stardust-V1 Authentication Configuration
JWT_AUTH_BASE_URL=https://stardust-v1.my-firstcare.com
ENABLE_JWT_AUTH=true
## following Stardust-V1 documentation for more details Stardust-V1 Centralized JWT Authentication Handbook.md

# Development Authentication Bypass (SECURITY WARNING)
ENABLE_AUTH_BYPASS=true  # Enabled for development - DISABLE IN PRODUCTION

# Application URLs
ADMIN_PANEL_URL=https://opera.my-firstcare.com
API_URL=https://stardust.my-firstcare.com

# TTL Configuration (in seconds)
AUDIT_LOG_TTL=15552000  # 180 days
FHIR_LOG_TTL=15552000   # 180 days

# Security
CORS_ORIGINS=*
API_KEY_HEADER=X-API-Key

# Patient Data Security (CRITICAL - Change in Production)
PATIENT_ENCRYPTION_PASSWORD=Sim!44335599
PATIENT_ENCRYPTION_SALT=Sim!44335599
PATIENT_HASH_SALT=Sim!44335599
# Optional: Use base64 encoded key instead of password/salt
# PATIENT_ENCRYPTION_KEY=base64-encoded-fernet-key


## 🧠 Notes
- Stardust credentials are required for role-based login