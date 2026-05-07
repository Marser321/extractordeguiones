from pathlib import Path
from typing import Optional

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings

class TranscriptionService:
    def __init__(self):
        self.model_size = settings.WHISPER_MODEL
        self.device = settings.WHISPER_DEVICE
        self.model: Optional[WhisperModel] = None

    def _get_model(self) -> WhisperModel:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper no está instalado. Instala requirements-local.txt para transcripción local.")
        if self.model is None:
            device = self.device
            compute_type = "int8"
            
            if device == "auto":
                # Por ahora faster-whisper en Mac usa CPU mayoritariamente
                # En Linux/Windows con NVIDIA usaría cuda.
                device = "cpu"
                
            print(f"[Whisper] Cargando modelo '{self.model_size}' en dispositivo '{device}'...")
            # Se carga bajo demanda para que la UI y la API arranquen rapido.
            self.model = WhisperModel(self.model_size, device=device, compute_type=compute_type)
        return self.model

    def transcribe_audio(self, audio_path: Path, language: str = "es") -> dict:
        """
        Transcribe el archivo de audio usando Faster Whisper o Gemini Cloud (con fallback).
        """
        if settings.USE_CLOUD_PIPELINE:
            try:
                return self.transcribe_cloud(audio_path)
            except Exception as e:
                print(f"⚠️ Cloud Pipeline falló ({e}). Usando fallback local...")
            
        return self.transcribe_local(audio_path, language=language)

    def transcribe_local(self, audio_path: Path, language: str = "es") -> dict:
        """Transcribe usando el modelo local (Whisper)."""
        model = self._get_model()
        segments, info = model.transcribe(str(audio_path), language=language)
        
        full_text = ""
        structured_segments = []
        
        for segment in segments:
            full_text += segment.text + " "
            structured_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
            
        return {
            "language_detected": info.language,
            "language_probability": info.language_probability,
            "full_text": full_text.strip(),
            "segments": structured_segments,
            "provider": "whisper_local"
        }

    def transcribe_cloud(self, audio_path: Path) -> dict:
        """Transcribe usando Gemini Cloud (Zero CPU load)."""
        try:
            from services.ai_provider_service import ai_provider_service
        except ModuleNotFoundError:
            from backend.services.ai_provider_service import ai_provider_service
            
        # 1. Subir a la nube
        cloud_file = ai_provider_service.upload_to_cloud(audio_path, mime_type="audio/wav")
        
        # 2. Solicitar transcripción
        prompt = """
        Transcribe este audio íntegramente. 
        Responde exclusivamente en JSON con esta estructura:
        {
          "full_text": "el texto completo",
          "language": "es"
        }
        """
        result = ai_provider_service.generate_cloud_json(prompt, [cloud_file])
        
        return {
            "language_detected": result.get("language", "es"),
            "language_probability": 1.0,
            "full_text": result.get("full_text", ""),
            "segments": [], # Gemini no devuelve segmentos por defecto fácilmente
            "provider": "gemini_cloud"
        }

transcription_service = TranscriptionService()
