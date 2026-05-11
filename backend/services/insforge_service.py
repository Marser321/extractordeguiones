import requests
import json
import time
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings

class InsForgeService:
    def __init__(self):
        self.base_url = settings.INSFORGE_BASE_URL
        self.anon_key = settings.INSFORGE_ANON_KEY
        self.headers = {
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def configured(self) -> bool:
        return bool(self.base_url and self.anon_key)

    def _get_url(self, table: str, params: Optional[Dict] = None) -> str:
        url = f"{self.base_url}/api/database/records/{table}"
        if params:
            query = urlencode(params)
            url = f"{url}?{query}"
        return url

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Helper para realizar peticiones con reintentos básicos."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, **kwargs)
                if response.status_code < 500: # No reintentar errores 4xx (cliente)
                    return response
                print(f"[InsForge] Intento {attempt + 1} falló: {response.status_code}")
            except Exception as e:
                print(f"[InsForge] Intento {attempt + 1} excepción: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1)) # Backoff simple
        
        # Último intento si fallaron todos los reintentos
        return requests.request(method, url, **kwargs)

    def create_video_script(
        self,
        brand_name: str,
        video_id: str,
        source_value: str,
        job_id: str,
        status: str = "pending",
        job_state: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict]:
        """Crea un registro inicial en la tabla video_scripts."""
        if not self.configured():
            return None
        url = self._get_url("video_scripts")
        payload = [{
            "brand_name": brand_name,
            "video_id_str": video_id,
            "video_url": source_value,
            "job_id": job_id,
            "status": status,
        }]
        if job_state:
            payload[0]["analyzed_script"] = json.dumps({"job_state": job_state}, ensure_ascii=False)
        
        try:
            response = self._request("POST", url, headers=self.headers, json=payload, timeout=20)
            if response.status_code in [200, 201]:
                return response.json()[0]
            print(f"[InsForge] Error creating record: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"[InsForge] Exception in create_video_script: {e}")
            return None

    def update_video_script(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza un registro existente."""
        if not self.configured():
            return False
        url = self._get_url("video_scripts", {"id": f"eq.{record_id}"})
        try:
            response = self._request("PATCH", url, headers=self.headers, json=updates, timeout=20)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"[InsForge] Exception in update_video_script: {e}")
            return False

    def update_video_script_by_job_id(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza un job por su identificador publico."""
        if not self.configured():
            return False
        url = self._get_url("video_scripts", {"job_id": f"eq.{job_id}"})
        try:
            response = self._request("PATCH", url, headers=self.headers, json=updates, timeout=20)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"[InsForge] Exception in update_video_script_by_job_id: {e}")
            return False

    def get_video_script_by_job_id(self, job_id: str) -> Optional[Dict]:
        if not self.configured():
            return None
        url = self._get_url("video_scripts", {"job_id": f"eq.{job_id}"})
        try:
            response = self._request("GET", url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                rows = response.json()
                return rows[0] if rows else None
            return None
        except Exception as e:
            print(f"[InsForge] Exception in get_video_script_by_job_id: {e}")
            return None

    def get_video_script(self, brand_name: str, video_id: str) -> Optional[Dict]:
        if not self.configured():
            return None
        url = self._get_url("video_scripts", {
            "brand_name": f"eq.{brand_name}",
            "video_id_str": f"eq.{video_id}",
        })
        try:
            response = self._request("GET", url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                rows = response.json()
                return rows[0] if rows else None
            return None
        except Exception as e:
            print(f"[InsForge] Exception in get_video_script: {e}")
            return None

    def get_scripts_by_brand(self, brand_name: str) -> List[Dict]:
        """Busca scripts persistidos por marca."""
        if not self.configured():
            return []
        url = self._get_url("video_scripts", {"brand_name": f"eq.{brand_name}"})
        try:
            response = self._request("GET", url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"[InsForge] Exception in get_scripts_by_brand: {e}")
            return []

    def log_memory(self, task_name: str, summary: str, metadata: Optional[Dict] = None):
        """Guarda un resumen de éxito en la memoria del orquestador."""
        url = self._get_url("orchestrator_memory")
        payload = [{
            "task_name": task_name,
            "summary": summary,
            "metadata": metadata or {}
        }]
        try:
            if self.configured():
                self._request("POST", url, headers=self.headers, json=payload, timeout=20)
        except Exception as e:
            print(f"[InsForge] Error logging memory: {e}")

    def create_or_update_brand(self, brand_data: Dict[str, Any]) -> bool:
        """Crea o actualiza un perfil de marca usando upsert (PostgREST style)."""
        url = self._get_url("brands")
        # PostgREST upsert requires Prefer: resolution=merge-duplicates
        headers = self.headers.copy()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        
        # Limpiar datos para que coincidan con el esquema de la base de datos
        clean_data = {
            "name": brand_data.get("name") or brand_data.get("brand_name"),
            "tone": brand_data.get("tone"),
            "audience": brand_data.get("audience"),
            "offer": brand_data.get("offer"),
            "visual_style": brand_data.get("visual_style"),
            "colors": brand_data.get("colors") if isinstance(brand_data.get("colors"), list) else [],
            "forbidden_words": brand_data.get("forbidden_words") if isinstance(brand_data.get("forbidden_words"), list) else [],
            "cta": brand_data.get("cta"),
            "preferred_formats": brand_data.get("preferred_formats") if isinstance(brand_data.get("preferred_formats"), list) else [],
            "metadata": brand_data.get("metadata", {})
        }
        
        try:
            if not self.configured():
                return False
            response = self._request("POST", url, headers=headers, json=[clean_data], timeout=20)
            if response.status_code not in [200, 201]:
                print(f"[InsForge] Error syncing brand: {response.status_code} - {response.text}")
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"[InsForge] Exception in create_or_update_brand: {e}")
            return False

    def get_brand(self, brand_name: str) -> Optional[Dict]:
        """Recupera un perfil de marca por nombre."""
        if not self.configured():
            return None
        url = self._get_url("brands", {"name": f"eq.{brand_name}"})
        try:
            response = self._request("GET", url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                rows = response.json()
                return rows[0] if rows else None
            return None
        except Exception as e:
            print(f"[InsForge] Exception in get_brand: {e}")
            return None

    def get_brand_profile(self, brand_name: str) -> Optional[Dict]:
        """Alias compatible con VaultService para recuperar perfiles de marca."""
        return self.get_brand(brand_name)

    def list_all_brands(self) -> List[Dict]:
        """Lista todas las marcas registradas."""
        if not self.configured():
            return []
        url = self._get_url("brands")
        try:
            response = self._request("GET", url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"[InsForge] Exception in list_all_brands: {e}")
            return []

    def list_brands_from_scripts(self) -> List[str]:
        """Obtiene nombres de marcas unicos desde la tabla de scripts (fallback)."""
        if not self.configured():
            return []
        # Usamos select con distinct a traves de select=brand_name
        url = self._get_url("video_scripts", {"select": "brand_name"})
        try:
            response = self._request("GET", url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                rows = response.json()
                return list(set(row["brand_name"] for row in rows if row.get("brand_name")))
            return []
        except Exception as e:
            print(f"[InsForge] Exception in list_brands_from_scripts: {e}")
            return []

insforge_service = InsForgeService()
