import os
import re
from typing import List, Optional, Union

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings

class ApiKeyService:
    def __init__(self):
        self.provider_state = {
            "gemini": {"keys": self._load_keys(settings.GEMINI_API_KEY, settings.GEMINI_API_KEYS), "current_index": 0, "exhausted": set()},
            "openrouter": {"keys": self._load_keys(settings.OPENROUTER_API_KEY, settings.OPENROUTER_API_KEYS), "current_index": 0, "exhausted": set()},
            "groq": {"keys": self._load_keys(settings.GROQ_API_KEY, settings.GROQ_API_KEYS), "current_index": 0, "exhausted": set()},
        }

    def _load_keys(self, main_key: str, multi_keys: str) -> List[str]:
        raw_keys = multi_keys.replace("\\n", "\n")
        keys = [key.strip() for key in re.split(r"[\s,;]+", raw_keys) if key.strip()]
        
        # Asegurar que la llave principal esté en la lista si no está ya
        if main_key and main_key not in keys:
            keys.insert(0, main_key)
            
        return keys

    def total_keys(self, provider: str = "gemini") -> int:
        state = self.provider_state.get(provider)
        return len(state["keys"]) if state else 0

    def available_keys(self, provider: str = "gemini") -> int:
        state = self.provider_state.get(provider)
        if not state:
            return 0
        return len([key for key in state["keys"] if key not in state["exhausted"]])

    def get_active_key(self, provider: str = "gemini") -> Optional[str]:
        """Devuelve la llave actual si no está agotada."""
        state = self.provider_state.get(provider)
        if not state or not state["keys"]:
            return None
            
        # Buscar la primera llave no agotada empezando por el índice actual
        for _ in range(len(state["keys"])):
            key = state["keys"][state["current_index"]]
            if key not in state["exhausted"]:
                return key
            state["current_index"] = (state["current_index"] + 1) % len(state["keys"])
            
        return None # Todas agotadas

    def rotate_key(self, provider: str = "gemini") -> Optional[str]:
        """Marca la llave actual como agotada y pasa a la siguiente."""
        state = self.provider_state.get(provider)
        if not state or self.available_keys(provider) == 0:
            return None
            
        current_key = state["keys"][state["current_index"]]
        print(f"[{provider.capitalize()}] Llave no utilizable detectada: {current_key[:8]}... Rotando.")
        state["exhausted"].add(current_key)
        
        # Pasar a la siguiente
        state["current_index"] = (state["current_index"] + 1) % len(state["keys"])
        return self.get_active_key(provider)

    def should_rotate_for_error(self, error: Union[Exception, str]) -> bool:
        """Detecta errores de llave recuperables con una rotacion."""
        message = str(error)
        markers = (
            "ResourceExhausted",
            "429",
            "API_KEY_INVALID",
            "API key not valid",
            "PERMISSION_DENIED",
            "reported as leaked",
            "has been blocked",
            "insufficient_quota",
            "rate_limit_exceeded"
        )
        return any(marker in message for marker in markers)

    def reset_exhausted(self, provider: Optional[str] = None):
        """Reinicia el estado de las llaves (útil para un nuevo día)."""
        providers = [provider] if provider else self.provider_state.keys()
        for p in providers:
            if p in self.provider_state:
                self.provider_state[p]["exhausted"].clear()
                self.provider_state[p]["current_index"] = 0

api_key_service = ApiKeyService()
