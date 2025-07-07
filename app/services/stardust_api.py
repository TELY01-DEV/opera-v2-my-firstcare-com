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

    # Master Data operations
    async def get_master_data(self, token: str, data_type: str, skip: int = 0, limit: int = 100, 
                             search: Optional[str] = None, province_code: Optional[int] = None, 
                             district_code: Optional[int] = None, is_active: Optional[bool] = None,
                             date_from: Optional[str] = None, date_to: Optional[str] = None):
        """Get master data by type"""
        # Map data types to actual Stardust endpoints (using working endpoints found)
        endpoint_mapping = {
            "provinces": "/admin/master-data/provinces",
            "districts": "/admin/master-data/districts", 
            "sub-districts": "/admin/master-data/sub_districts",  # Uses underscore
            "hospital-types": "/admin/master-data/hospital_types",  # Uses underscore
            "hospitals": "/admin/master-data/hospitals"
        }
        
        endpoint = endpoint_mapping.get(data_type, f"/admin/master-data/{data_type}")
        
        params: dict = {
            "skip": skip, 
            "limit": limit,
            "sort": "updated_at",  # Sort by last update time
            "order": "desc"       # Most recent first
        }
        if search:
            params["search"] = search
        if province_code:
            params["province_code"] = province_code
        if district_code:
            params["district_code"] = district_code
        if is_active is not None:
            params["is_active"] = is_active
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        return await self._make_request("GET", endpoint, token, params=params)

    async def get_master_data_record(self, token: str, data_type: str, record_id: str):
        """Get specific master data record"""
        endpoint_mapping = {
            "provinces": f"/admin/master-data/provinces/{record_id}",
            "districts": f"/admin/master-data/districts/{record_id}", 
            "sub-districts": f"/admin/master-data/sub_districts/{record_id}",  # Uses underscore
            "hospital-types": f"/admin/master-data/hospital_types/{record_id}",  # Uses underscore
            "hospitals": f"/admin/master-data/hospitals/{record_id}"
        }
        endpoint = endpoint_mapping.get(data_type, f"/admin/master-data/{data_type}/{record_id}")
        return await self._make_request("GET", endpoint, token)

    async def create_master_data(self, token: str, data: dict):
        """Create new master data record"""
        data_type = data.get("data_type", "")
        endpoint_mapping = {
            "provinces": "/admin/master-data/provinces",
            "districts": "/admin/master-data/districts", 
            "sub-districts": "/admin/master-data/sub_districts",  # Uses underscore
            "hospital-types": "/admin/master-data/hospital_types",  # Uses underscore
            "hospitals": "/admin/master-data/hospitals"
        }
        endpoint = endpoint_mapping.get(data_type, "/admin/master-data")
        return await self._make_request("POST", endpoint, token, data=data)

    async def update_master_data(self, token: str, data_type: str, record_id: str, data: dict):
        """Update master data record"""
        endpoint_mapping = {
            "provinces": f"/admin/master-data/provinces/{record_id}",
            "districts": f"/admin/master-data/districts/{record_id}", 
            "sub-districts": f"/admin/master-data/sub_districts/{record_id}",  # Uses underscore
            "hospital-types": f"/admin/master-data/hospital_types/{record_id}",  # Uses underscore
            "hospitals": f"/admin/master-data/hospitals/{record_id}"
        }
        endpoint = endpoint_mapping.get(data_type, f"/admin/master-data/{data_type}/{record_id}")
        return await self._make_request("PUT", endpoint, token, data=data)

    async def delete_master_data(self, token: str, data_type: str, record_id: str):
        """Soft delete master data record"""
        endpoint_mapping = {
            "provinces": f"/admin/master-data/provinces/{record_id}",
            "districts": f"/admin/master-data/districts/{record_id}", 
            "sub-districts": f"/admin/master-data/sub_districts/{record_id}",  # Uses underscore
            "hospital-types": f"/admin/master-data/hospital_types/{record_id}",  # Uses underscore
            "hospitals": f"/admin/master-data/hospitals/{record_id}"
        }
        endpoint = endpoint_mapping.get(data_type, f"/admin/master-data/{data_type}/{record_id}")
        return await self._make_request("DELETE", endpoint, token)

    # Province operations
    async def get_provinces(self, token: str, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        """Get list of provinces"""
        return await self.get_master_data(token, "provinces", skip, limit, search)

    async def get_province(self, token: str, province_id: str):
        """Get province by ID"""
        return await self.get_master_data_record(token, "provinces", province_id)

    async def create_province(self, token: str, province_data: dict):
        """Create new province"""
        province_data["data_type"] = "provinces"
        return await self.create_master_data(token, province_data)

    async def update_province(self, token: str, province_id: str, province_data: dict):
        """Update province"""
        return await self.update_master_data(token, "provinces", province_id, province_data)

    async def delete_province(self, token: str, province_id: str):
        """Delete province"""
        return await self.delete_master_data(token, "provinces", province_id)

    # District operations
    async def get_districts(self, token: str, skip: int = 0, limit: int = 100, search: Optional[str] = None, 
                           province_code: Optional[int] = None):
        """Get list of districts"""
        return await self.get_master_data(token, "districts", skip, limit, search, province_code)

    async def get_district(self, token: str, district_id: str):
        """Get district by ID"""
        return await self.get_master_data_record(token, "districts", district_id)

    async def create_district(self, token: str, district_data: dict):
        """Create new district"""
        district_data["data_type"] = "districts"
        return await self.create_master_data(token, district_data)

    async def update_district(self, token: str, district_id: str, district_data: dict):
        """Update district"""
        return await self.update_master_data(token, "districts", district_id, district_data)

    async def delete_district(self, token: str, district_id: str):
        """Delete district"""
        return await self.delete_master_data(token, "districts", district_id)

    # Sub-District operations
    async def get_sub_districts(self, token: str, skip: int = 0, limit: int = 100, search: Optional[str] = None, 
                               province_code: Optional[int] = None, district_code: Optional[int] = None):
        """Get list of sub-districts"""
        return await self.get_master_data(token, "sub-districts", skip, limit, search, province_code, district_code)

    async def get_sub_district(self, token: str, sub_district_id: str):
        """Get sub-district by ID"""
        return await self.get_master_data_record(token, "sub-districts", sub_district_id)

    async def create_sub_district(self, token: str, sub_district_data: dict):
        """Create new sub-district"""
        sub_district_data["data_type"] = "sub-districts"
        return await self.create_master_data(token, sub_district_data)

    async def update_sub_district(self, token: str, sub_district_id: str, sub_district_data: dict):
        """Update sub-district"""
        return await self.update_master_data(token, "sub-districts", sub_district_id, sub_district_data)

    async def delete_sub_district(self, token: str, sub_district_id: str):
        """Delete sub-district"""
        return await self.delete_master_data(token, "sub-districts", sub_district_id)

    # Hospital Type operations
    async def get_hospital_types(self, token: str, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        """Get list of hospital types"""
        return await self.get_master_data(token, "hospital-types", skip, limit, search)

    async def get_hospital_type(self, token: str, hospital_type_id: str):
        """Get hospital type by ID"""
        return await self.get_master_data_record(token, "hospital-types", hospital_type_id)

    async def create_hospital_type(self, token: str, hospital_type_data: dict):
        """Create new hospital type"""
        hospital_type_data["data_type"] = "hospital-types"
        return await self.create_master_data(token, hospital_type_data)

    async def update_hospital_type(self, token: str, hospital_type_id: str, hospital_type_data: dict):
        """Update hospital type"""
        return await self.update_master_data(token, "hospital-types", hospital_type_id, hospital_type_data)

    async def delete_hospital_type(self, token: str, hospital_type_id: str):
        """Delete hospital type"""
        return await self.delete_master_data(token, "hospital-types", hospital_type_id)

    # Enhanced Hospital operations with master data support
    async def create_hospital(self, token: str, hospital_data: dict):
        """Create new hospital"""
        hospital_data["data_type"] = "hospitals"
        return await self.create_master_data(token, hospital_data)

    async def update_hospital(self, token: str, hospital_id: str, hospital_data: dict):
        """Update hospital"""
        return await self.update_master_data(token, "hospitals", hospital_id, hospital_data)

    async def delete_hospital(self, token: str, hospital_id: str):
        """Delete hospital"""
        return await self.delete_master_data(token, "hospitals", hospital_id)


# Global instance
stardust_api = StardustAPIService()
