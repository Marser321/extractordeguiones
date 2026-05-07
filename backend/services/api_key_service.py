import os
from typing import List, Optional

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings

class ApiKeyService:
    def __init__(self):
        self.keys = self._load_keys()
        self.current_index = 0
        self.exhausted_keys = set()

    def _load_keys(self) -> List[str]:
        # Cargar llave principal y llaves secundarias
        raw_keys = settings.GEMINI_API_KEYS
        keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        
        # Asegurar que la llave principal esté en la lista si no está ya
        main_key = settings.GEMINI_API_KEY
        if main_key and main_key not in keys:
            keys.insert(0, main_key)
            
        return keys

    def get_active_key(self) -> Optional[str]:
        """Devuelve la llave actual si no está agotada."""
        if not self.keys:
            return settings.GEMINI_API_KEY
            
        # Buscar la primera llave no agotada empezando por el índice actual
        for _ in range(len(self.keys)):
            key = self.keys[self.current_index]
            if key not in self.exhausted_keys:
                return key
            self.current_index = (self.current_index + 1) % len(self.keys)
            
        return None # Todas agotadas

    def rotate_key(self) -> Optional[str]:
        """Marca la llave actual como agotada y pasa a la siguiente."""
        if not self.keys:
            return None
            
        current_key = self.keys[self.current_index]
        print(f"⚠️ Llave agotada detectada: {current_key[:8]}... Rotando.")
        self.exhausted_keys.add(current_key)
        
        # Pasar a la siguiente
        self.current_index = (self.current_index + 1) % len(self.keys)
        return self.get_active_key()

    def reset_exhausted(self):
        """Reinicia el estado de las llaves (útil para un nuevo día)."""
        self.exhausted_keys.clear()
        self.current_index = 0

api_key_service = ApiKeyService()
