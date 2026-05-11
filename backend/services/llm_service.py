from typing import Optional

import requests

try:
    import google.generativeai as legacy_genai
except Exception:
    legacy_genai = None

try:
    from google import genai
except Exception:
    genai = None

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings


def _get_api_key_service():
    try:
        from services.api_key_service import api_key_service
    except ModuleNotFoundError:
        from backend.services.api_key_service import api_key_service
    return api_key_service


class LLMService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL
        
        self.gemini_model_name = settings.GEMINI_DEFAULT_MODEL
        self.gemini_pro_model_name = settings.GEMINI_PRO_MODEL

    def _get_gemini_client(self, api_key: Optional[str] = None):
        """Obtiene un cliente o modelo configurado dinámicamente."""
        api_key_service = _get_api_key_service()
        key = api_key or api_key_service.get_active_key()
        
        if not key:
            return None, None
            
        if genai is not None:
            client = genai.Client(api_key=key)
            return client, None
        elif legacy_genai is not None:
            legacy_genai.configure(api_key=key)
            return None, legacy_genai
        return None, None

    def has_gemini(self) -> bool:
        api_key_service = _get_api_key_service()
        return bool(api_key_service.get_active_key())

    def generate_with_ollama(self, prompt: str, model: str = None) -> str:
        """Llama a la API local de Ollama."""
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(f"{self.ollama_url}/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            return f"Error conectando con Ollama: {str(e)}"

    def generate_with_gemini(self, prompt: str, use_pro: bool = False) -> str:
        """Llama a la API de Gemini dinámicamente."""
        client, legacy = self._get_gemini_client()
        if not client and not legacy:
            return "Error: GEMINI_API_KEY no configurada o no disponible."
        
        target_model = self.gemini_pro_model_name if use_pro else self.gemini_model_name
        
        try:
            if client is not None:
                response = client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                )
                return getattr(response, "text", "") or ""
            
            # Legacy GenAI
            model_instance = legacy.GenerativeModel(target_model)
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            api_key_service = _get_api_key_service()
            if api_key_service.should_rotate_for_error(e):
                if api_key_service.rotate_key():
                    return self.generate_with_gemini(prompt, use_pro=use_pro)
            return f"Error conectando con Gemini: {str(e)}"

llm_service = LLMService()
