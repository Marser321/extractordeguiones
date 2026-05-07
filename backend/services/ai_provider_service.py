from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from PIL import Image
except ImportError:
    Image = None

import requests

try:
    from google import genai
    from google.genai import types as genai_types
except Exception:
    genai = None
    genai_types = None

try:
    import google.generativeai as legacy_genai
except Exception:
    legacy_genai = None

try:
    from core.config import settings
    from services.ollama_control_service import ollama_control_service
    from services.api_key_service import api_key_service
except ModuleNotFoundError:
    from backend.core.config import settings
    from backend.services.ollama_control_service import ollama_control_service
    from backend.services.api_key_service import api_key_service


class AIProviderService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.ollama_default_model = settings.OLLAMA_DEFAULT_MODEL
        self.gemini_default_model = settings.GEMINI_DEFAULT_MODEL
        self.gemini_pro_model = settings.GEMINI_PRO_MODEL

    def status(self) -> dict:
        ollama_models = self._ollama_models()
        ollama_control = ollama_control_service.status()
        return {
            "default_provider": settings.AI_DEFAULT_PROVIDER,
            "fallback_provider": settings.AI_FALLBACK_PROVIDER,
            "ollama": {
                "available": ollama_models is not None and ollama_control["running"],
                "base_url": self.ollama_url,
                "default_model": self.ollama_default_model,
                "models": ollama_models or [],
                "control": ollama_control,
                "running": ollama_control["running"],
                "pid": ollama_control["pid"],
                "launchd_service": ollama_control["launchd_service"],
                "can_start": ollama_control["can_start"],
                "can_stop": ollama_control["can_stop"],
            },
            "gemini": {
                "available": bool(settings.GEMINI_API_KEY and (genai is not None or legacy_genai is not None)),
                "configured": bool(settings.GEMINI_API_KEY),
                "sdk_installed": genai is not None,
                "legacy_sdk_installed": legacy_genai is not None,
                "default_model": self.gemini_default_model,
                "models": [self.gemini_default_model, self.gemini_pro_model],
            },
        }

    def models(self) -> dict:
        status = self.status()
        return {
            "ollama": status["ollama"]["models"],
            "gemini": status["gemini"]["models"] if status["gemini"]["configured"] else [],
        }

    def generate_text(self, prompt: str, provider: str, model: Optional[str] = None, json_mode: bool = False) -> str:
        if provider == "gemini":
            return self._generate_gemini(prompt, model or self.gemini_default_model, json_mode=json_mode)
        if provider == "ollama":
            return self._generate_ollama(prompt, model or self.ollama_default_model, json_mode=json_mode)
        raise ValueError(f"Proveedor IA no soportado: {provider}")

    def generate_vision_json(self, prompt: str, image_paths: list[Path], provider: str = "gemini", model: Optional[str] = None) -> dict:
        if provider != "gemini":
            # Por ahora solo Gemini soporta visión en esta implementación
            raise ValueError(f"Visión no soportada para proveedor: {provider}")
        
        text = self._generate_gemini_vision(prompt, image_paths, model or self.gemini_default_model, json_mode=True)
        parsed = self._parse_json(text)
        parsed["_ai_provider"] = provider
        parsed["_ai_model"] = model or self.default_model_for(provider)
        return parsed

    def generate_json(self, prompt: str, provider: str = "ollama", model: Optional[str] = None, fallback_provider: Optional[str] = None) -> dict:
        """Genera JSON estructurado usando el proveedor indicado."""
        try:
            if provider == "gemini":
                return self.generate_gemini_json(prompt, model=model)
            return self.generate_ollama_json(prompt, model=model)
        except Exception as e:
            # Detectar ResourceExhausted para rotar llave
            if "ResourceExhausted" in str(e) or "429" in str(e):
                new_key = api_key_service.rotate_key()
                if new_key:
                    print(f"🔄 Reintentando con nueva llave API...")
                    return self.generate_json(prompt, provider=provider, model=model, fallback_provider=fallback_provider)
            
            if fallback_provider and fallback_provider != provider:
                print(f"⚠️ Error en {provider}: {e}. Usando fallback {fallback_provider}...")
                return self.generate_json(prompt, provider=fallback_provider, model=model)
            raise e

    def default_model_for(self, provider: str) -> str:
        if provider == "gemini":
            return self.gemini_default_model
        return self.ollama_default_model

    def upload_to_cloud(self, file_path: Path, mime_type: Optional[str] = None) -> Any:
        """Sube un archivo a Gemini Cloud para procesamiento nativo."""
        api_key = api_key_service.get_active_key() or settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada.")
        
        if legacy_genai is not None:
            legacy_genai.configure(api_key=api_key)
            print(f"[Gemini Cloud] Subiendo archivo: {file_path.name}...")
            return legacy_genai.upload_file(str(file_path), mime_type=mime_type)
        
        raise RuntimeError("SDK Gemini legacy (google-generativeai) no disponible para subida de archivos.")

    def generate_multimodal(self, prompt: str, files: list[Any], model: Optional[str] = None, json_mode: bool = False) -> str:
        """Genera contenido a partir de múltiples archivos (audio/video/imágenes) en la nube."""
        api_key = api_key_service.get_active_key()
        if not api_key:
            raise RuntimeError("No hay llaves Gemini API disponibles para multimodal.")
            
        target_model = model or self.gemini_default_model
        
        try:
            if legacy_genai is not None:
                legacy_genai.configure(api_key=api_key)
                model_instance = legacy_genai.GenerativeModel(target_model)
                
                contents = [prompt] + files
                
                print(f"[Gemini Cloud] Generando análisis multimodal con {target_model}...")
                response = model_instance.generate_content(contents)
                return getattr(response, "text", "") or ""
                
            raise RuntimeError("SDK Gemini legacy no disponible para generación multimodal.")
        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):
                if api_key_service.rotate_key():
                    print(f"🔄 [Gemini Multimodal] Cuota agotada. Rotando y reintentando...")
                    return self.generate_multimodal(prompt, files, model=model, json_mode=json_mode)
            raise e

    def generate_gemini_json(self, prompt: str, model: Optional[str] = None) -> dict:
        """Genera JSON usando Gemini (google-generativeai legacy)."""
        api_key = api_key_service.get_active_key()
        if not api_key:
            raise RuntimeError("No hay llaves Gemini API disponibles para JSON.")
            
        target_model = model or self.gemini_default_model
        
        try:
            if legacy_genai is not None:
                legacy_genai.configure(api_key=api_key)
                model_instance = legacy_genai.GenerativeModel(target_model)
                
                print(f"[Gemini] Generando JSON con {target_model}...")
                response = model_instance.generate_content(
                    prompt,
                    generation_config=legacy_genai.types.GenerationConfig(
                        response_mime_type="application/json",
                    )
                )
                return self._parse_json(response.text)
                
            raise RuntimeError("SDK Gemini legacy no disponible.")
        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):
                if api_key_service.rotate_key():
                    print(f"🔄 [Gemini JSON] Cuota agotada. Rotando y reintentando...")
                    return self.generate_gemini_json(prompt, model=model)
            raise e

    def generate_ollama_json(self, prompt: str, model: Optional[str] = None) -> dict:
        """Genera JSON usando Ollama local."""
        text = self._generate_ollama(prompt, model or self.ollama_default_model, json_mode=True)
        return self._parse_json(text)

    def generate_cloud_json(self, prompt: str, files: list[Any], model: Optional[str] = None) -> dict:
        """Genera JSON a partir de contenido multimodal en la nube."""
        text = self.generate_multimodal(prompt, files, model=model, json_mode=True)
        return self._parse_json(text)

    def _ollama_models(self) -> Optional[list]:
        try:
            response = requests.get(f"{self.ollama_url}/tags", timeout=4)
            response.raise_for_status()
            data = response.json()
            return [item.get("name") for item in data.get("models", []) if item.get("name")]
        except requests.RequestException:
            return None

    def _generate_ollama(self, prompt: str, model: str, json_mode: bool = False) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.2},
        }
        if json_mode:
            payload["format"] = "json"

        response = requests.post(f"{self.ollama_url}/chat", json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")

    def _generate_gemini(self, prompt: str, model: str, json_mode: bool = False) -> str:
        api_key = api_key_service.get_active_key()
        if not api_key:
            raise RuntimeError("No hay llaves Gemini API disponibles (todas agotadas o no configuradas).")

        try:
            if genai is not None:
                client = genai.Client(api_key=api_key)
                config = None
                if json_mode and genai_types is not None:
                    config = genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                return getattr(response, "text", "") or ""

            if legacy_genai is not None:
                legacy_genai.configure(api_key=api_key)
                legacy_model = legacy_genai.GenerativeModel(model)
                response = legacy_model.generate_content(prompt)
                return getattr(response, "text", "") or ""
                
        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):
                if api_key_service.rotate_key():
                    print(f"🔄 [Gemini] Cuota agotada. Rotando y reintentando...")
                    return self._generate_gemini(prompt, model, json_mode=json_mode)
            raise e

        raise RuntimeError("No hay SDK Gemini instalado. Instala google-genai o google-generativeai.")

    def _generate_gemini_vision(self, prompt: str, image_paths: list[Path], model: str, json_mode: bool = False) -> str:
        api_key = api_key_service.get_active_key()
        if not api_key:
            raise RuntimeError("No hay llaves Gemini API disponibles para visión.")

        try:
            if genai is not None:
                client = genai.Client(api_key=api_key)
                config = None
                if json_mode and genai_types is not None:
                    config = genai_types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2,
                    )

                contents = [prompt]
                for path in image_paths:
                    if Image:
                        img = Image.open(path)
                        contents.append(img)
                    else:
                        # Fallback si no hay PIL, aunque genai prefiere objetos PIL o bytes
                        with open(path, "rb") as f:
                            contents.append(genai_types.Part.from_bytes(data=f.read(), mime_type="image/jpeg"))

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                return getattr(response, "text", "") or ""

            if legacy_genai is not None:
                legacy_genai.configure(api_key=api_key)
                legacy_model = legacy_genai.GenerativeModel(model)
                
                contents = [prompt]
                for path in image_paths:
                    if Image:
                        img = Image.open(path)
                        contents.append(img)
                    else:
                        with open(path, "rb") as f:
                            contents.append({"mime_type": "image/jpeg", "data": f.read()})
                
                response = legacy_model.generate_content(contents)
                return getattr(response, "text", "") or ""

        except Exception as e:
            if "ResourceExhausted" in str(e) or "429" in str(e):
                if api_key_service.rotate_key():
                    print(f"🔄 [Gemini Vision] Cuota agotada. Rotando y reintentando...")
                    return self._generate_gemini_vision(prompt, image_paths, model, json_mode=json_mode)
            raise e

        raise RuntimeError("No hay SDK Gemini instalado.")

    def _parse_json(self, text: str) -> dict:
        clean_text = text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`").strip()
            if clean_text.lower().startswith("json"):
                clean_text = clean_text[4:].strip()

        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            start = clean_text.find("{")
            end = clean_text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(clean_text[start : end + 1])
            raise


ai_provider_service = AIProviderService()
