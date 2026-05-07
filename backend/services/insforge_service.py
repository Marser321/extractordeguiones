import requests
from typing import Optional, List, Dict, Any
from core.config import settings

class InsForgeService:
    def __init__(self):
        self.base_url = settings.INSFORGE_BASE_URL
        self.anon_key = settings.INSFORGE_ANON_KEY
        self.headers = {
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def _get_url(self, table: str, params: Optional[Dict] = None) -> str:
        url = f"{self.base_url}/api/database/records/{table}"
        if params:
            query = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query}"
        return url

    def create_video_script(self, brand_name: str, video_id: str, source_value: str, job_id: str, status: str = "pending") -> Optional[Dict]:
        """Crea un registro inicial en la tabla video_scripts."""
        url = self._get_url("video_scripts")
        payload = [{
            "brand_name": brand_name,
            "video_id_str": video_id,
            "video_url": source_value,
            "job_id": job_id,
            "status": status
        }]
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code in [200, 201]:
                return response.json()[0]
            print(f"[InsForge] Error creating record: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"[InsForge] Exception in create_video_script: {e}")
            return None

    def update_video_script(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza un registro existente."""
        url = self._get_url("video_scripts", {"id": f"eq.{record_id}"})
        try:
            response = requests.patch(url, headers=self.headers, json=updates)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"[InsForge] Exception in update_video_script: {e}")
            return False

    def get_scripts_by_brand(self, brand_name: str) -> List[Dict]:
        """Simulación de búsqueda por marca (asumiendo que brand_name está en un campo o metadata)."""
        # Por ahora buscaremos todos
        url = self._get_url("video_scripts")
        try:
            response = requests.get(url, headers=self.headers)
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
            requests.post(url, headers=self.headers, json=payload)
        except Exception as e:
            print(f"[InsForge] Error logging memory: {e}")

    def create_or_update_brand(self, brand_data: Dict[str, Any]) -> bool:
        """Crea o actualiza un perfil de marca usando upsert (PostgREST style)."""
        url = self._get_url("brands")
        # PostgREST upsert requires Prefer: resolution=merge-duplicates
        headers = self.headers.copy()
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
        
        try:
            # Asegurarse de que el cuerpo sea un array para POST (upsert)
            response = requests.post(url, headers=headers, json=[brand_data])
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"[InsForge] Exception in create_or_update_brand: {e}")
            return False

    def get_brand(self, brand_name: str) -> Optional[Dict]:
        """Recupera un perfil de marca por nombre."""
        url = self._get_url("brands", {"name": f"eq.{brand_name}"})
        try:
            response = requests.get(url, headers=self.headers)
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
        url = self._get_url("brands")
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"[InsForge] Exception in list_all_brands: {e}")
            return []

insforge_service = InsForgeService()
