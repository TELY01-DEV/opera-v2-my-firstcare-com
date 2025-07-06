"""
Stardust API service for data operations
"""
import httpx
import os
from typing import List, Optional
from fastapi import HTTPException

class StardustAPIService:
    def __init__(self):
        self.base_url = os.getenv("STARDUST_API_BASE_URL", "https://stardust.my-firstcare.com")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _make_request(self, method: str, endpoint: str, token: str, data: Optional[dict] = None, params: Optional[dict] = None):
        """Make authenticated request to Stardust API"""
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Authentication failed")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="Access forbidden")
            elif response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=f"API error: {response.text}")
            
            return response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Stardust API service unavailable: {str(e)}")

    # Patient operations
    async def get_patients(self, token: str, skip: int = 0, limit: int = 100):
        """Get list of patients"""
        return await self._make_request("GET", "/patients", token, params={"skip": skip, "limit": limit})

    async def get_patient(self, token: str, patient_id: str):
        """Get patient by ID"""
        return await self._make_request("GET", f"/patients/{patient_id}", token)

    async def create_patient(self, token: str, patient_data: dict):
        """Create new patient"""
        return await self._make_request("POST", "/patients", token, data=patient_data)

    async def update_patient(self, token: str, patient_id: str, patient_data: dict):
        """Update patient"""
        return await self._make_request("PUT", f"/patients/{patient_id}", token, data=patient_data)

    async def delete_patient(self, token: str, patient_id: str):
        """Delete patient"""
        return await self._make_request("DELETE", f"/patients/{patient_id}", token)

    # AVA4 device operations
    async def get_ava4_devices(self, token: str, skip: int = 0, limit: int = 100):
        """Get list of AVA4 devices"""
        return await self._make_request("GET", "/devices/ava4", token, params={"skip": skip, "limit": limit})

    async def get_ava4_device(self, token: str, device_id: str):
        """Get AVA4 device by ID"""
        return await self._make_request("GET", f"/devices/ava4/{device_id}", token)

    async def create_ava4_device(self, token: str, device_data: dict):
        """Create new AVA4 device"""
        return await self._make_request("POST", "/devices/ava4", token, data=device_data)

    async def update_ava4_device(self, token: str, device_id: str, device_data: dict):
        """Update AVA4 device"""
        return await self._make_request("PUT", f"/devices/ava4/{device_id}", token, data=device_data)

    async def delete_ava4_device(self, token: str, device_id: str):
        """Delete AVA4 device"""
        return await self._make_request("DELETE", f"/devices/ava4/{device_id}", token)

    # Kati device operations
    async def get_kati_devices(self, token: str, skip: int = 0, limit: int = 100):
        """Get list of Kati devices"""
        return await self._make_request("GET", "/devices/kati", token, params={"skip": skip, "limit": limit})

    async def get_kati_device(self, token: str, device_id: str):
        """Get Kati device by ID"""
        return await self._make_request("GET", f"/devices/kati/{device_id}", token)

    async def create_kati_device(self, token: str, device_data: dict):
        """Create new Kati device"""
        return await self._make_request("POST", "/devices/kati", token, data=device_data)

    async def update_kati_device(self, token: str, device_id: str, device_data: dict):
        """Update Kati device"""
        return await self._make_request("PUT", f"/devices/kati/{device_id}", token, data=device_data)

    async def delete_kati_device(self, token: str, device_id: str):
        """Delete Kati device"""
        return await self._make_request("DELETE", f"/devices/kati/{device_id}", token)

    # Qube-Vital device operations
    async def get_qube_vital_devices(self, token: str, skip: int = 0, limit: int = 100):
        """Get list of Qube-Vital devices"""
        return await self._make_request("GET", "/devices/qube-vital", token, params={"skip": skip, "limit": limit})

    async def get_qube_vital_device(self, token: str, device_id: str):
        """Get Qube-Vital device by ID"""
        return await self._make_request("GET", f"/devices/qube-vital/{device_id}", token)

    async def create_qube_vital_device(self, token: str, device_data: dict):
        """Create new Qube-Vital device"""
        return await self._make_request("POST", "/devices/qube-vital", token, data=device_data)

    async def update_qube_vital_device(self, token: str, device_id: str, device_data: dict):
        """Update Qube-Vital device"""
        return await self._make_request("PUT", f"/devices/qube-vital/{device_id}", token, data=device_data)

    async def delete_qube_vital_device(self, token: str, device_id: str):
        """Delete Qube-Vital device"""
        return await self._make_request("DELETE", f"/devices/qube-vital/{device_id}", token)

    # Hospital operations
    async def get_hospitals(self, token: str, skip: int = 0, limit: int = 100):
        """Get list of hospitals"""
        return await self._make_request("GET", "/hospitals", token, params={"skip": skip, "limit": limit})

    async def get_hospital(self, token: str, hospital_id: str):
        """Get hospital by ID"""
        return await self._make_request("GET", f"/hospitals/{hospital_id}", token)

    # Analytics operations
    async def get_patient_count(self, token: str):
        """Get total patient count"""
        return await self._make_request("GET", "/stats/patient-count", token)

    async def get_device_usage(self, token: str):
        """Get device usage statistics"""
        return await self._make_request("GET", "/stats/device-usage", token)

    async def get_vital_trends(self, token: str, patient_id: Optional[str] = None, days: int = 7):
        """Get vital sign trends"""
        params: dict = {"days": str(days)}
        if patient_id:
            params["patient_id"] = patient_id
        return await self._make_request("GET", "/stats/vital-trends", token, params=params)

    async def get_alerts(self, token: str, alert_type: Optional[str] = None, since: str = "24h"):
        """Get system alerts"""
        params = {"since": since}
        if alert_type:
            params["type"] = alert_type
        return await self._make_request("GET", "/stats/alerts", token, params=params)

    # Audit log operations
    async def get_audit_logs(self, token: str, skip: int = 0, limit: int = 100):
        """Get FHIR audit logs"""
        return await self._make_request("GET", "/audit-logs", token, params={"skip": skip, "limit": limit})

# Global service instance
stardust_api = StardustAPIService()
