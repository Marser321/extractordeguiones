import subprocess
import shutil
from pathlib import Path
from typing import List

try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None

try:
    from core.config import settings
    from services.vault_service import vault_service
except ModuleNotFoundError:
    from backend.core.config import settings
    from backend.services.vault_service import vault_service

class VisualService:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffmpeg_available = self.ffmpeg_path is not None and self._check_ffmpeg()

    def _find_ffmpeg(self):
        binary = shutil.which("ffmpeg")
        if binary:
            return binary
        if imageio_ffmpeg is not None:
            try:
                return imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                return None
        return None

    def _check_ffmpeg(self) -> bool:
        if not self.ffmpeg_path:
            return False
        try:
            subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _ensure_ffmpeg(self):
        if not self.ffmpeg_available:
            self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path or not self._check_ffmpeg():
            raise RuntimeError("FFmpeg no está instalado. Requerido para extracción visual.")
        self.ffmpeg_available = True

    def extract_frames(self, video_file: Path, brand_name: str, video_id: str, interval_seconds: int = 10) -> List[Path]:
        """
        Extrae frames del video cada X segundos y los guarda en el Vault.
        """
        if try_cloud := getattr(settings, "USE_CLOUD_PIPELINE", False):
            print("[Visual] Cloud Pipeline activado: saltando extracción local de frames.")
            return []
            
        if not video_file.exists():
            raise FileNotFoundError(f"No se encontró el video: {video_file}")
        self._ensure_ffmpeg()

        frames_dir = vault_service.create_frames_dir(brand_name, video_id)
        
        # Limpiar frames anteriores si existen para evitar basura
        for f in frames_dir.glob("*.jpg"):
            f.unlink()

        # ffmpeg -i video.mp4 -vf "fps=1/10" -q:v 2 frames/frame_%03d.jpg
        # fps=1/10 extrae 1 frame cada 10 segundos.
        output_pattern = frames_dir / "frame_%03d.jpg"
        
        command = [
            self.ffmpeg_path,
            "-i", str(video_file),
            "-vf", f"fps=1/{interval_seconds}",
            "-q:v", "2", # Alta calidad (1-31, menor es mejor)
            str(output_pattern)
        ]

        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error extrayendo frames: {e.stderr.decode()}")

        return sorted(list(frames_dir.glob("*.jpg")))

    def analyze_frames(self, brand_name: str, video_id: str, script_text: str, provider: str = "gemini") -> dict:
        """
        Analiza una selección de frames extraídos o el video completo en la nube (con fallback).
        """
        if getattr(settings, "USE_CLOUD_PIPELINE", False):
            try:
                cloud_res = self.analyze_cloud_video(brand_name, video_id, script_text)
                if cloud_res.get("status") != "error":
                    return cloud_res
                print(f"⚠️ Cloud Video Status Error: {cloud_res.get('error')}. Usando fallback local...")
            except Exception as e:
                print(f"⚠️ Cloud Video Pipeline falló ({e}). Usando fallback local...")
            
        frames_dir = vault_service.get_video_path(brand_name, video_id) / "Frames"
        if not frames_dir.exists():
            return {"status": "no_frames_found", "error": "No hay frames para analizar."}

        # Seleccionamos hasta 5 frames distribuidos para no saturar el contexto
        all_frames = sorted(list(frames_dir.glob("*.jpg")))
        if not all_frames:
             return {"status": "empty_frames", "error": "No se encontraron archivos JPG en la carpeta Frames."}
        
        step = max(1, len(all_frames) // 5)
        selected_frames = all_frames[::step][:5]

        prompt = f"""
        Analiza estos frames de un video y el guion proporcionado.
        
        Guion: {script_text[:2000]}
        
        Describe:
        1. Escenario y estética general.
        2. Elementos visuales clave (objetos, personas, texto en pantalla).
        3. Estilo de edición (dinámico, cinemático, etc).
        4. Recomendaciones visuales para marketing basadas en lo que ves.

        Responde exclusivamente en JSON con esta estructura:
        {{
          "escenario": "descripción",
          "elementos_clave": ["elemento"],
          "estilo_visual": "descripción",
          "sugerencias_creativas": ["sugerencia"],
          "ocr_detectado": ["texto detectado en frames"]
        }}
        """.strip()

        try:
            from services.ai_provider_service import ai_provider_service
        except ModuleNotFoundError:
            from backend.services.ai_provider_service import ai_provider_service

        try:
            return ai_provider_service.generate_vision_json(prompt, selected_frames, provider=provider)
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def analyze_cloud_video(self, brand_name: str, video_id: str, script_text: str) -> dict:
        """Analiza el video nativamente en Gemini Cloud (Zero CPU)."""
        try:
            from services.ai_provider_service import ai_provider_service
        except ModuleNotFoundError:
            from backend.services.ai_provider_service import ai_provider_service
            
        # 1. Buscar el video original
        video_path = vault_service.get_video_path(brand_name, video_id) / "original_video"
        video_files = list(video_path.glob("*.mp4")) + list(video_path.glob("*.mov"))
        if not video_files:
            return {"status": "error", "error": "No se encontró el video original para subir a la nube."}
        
        # 2. Subir a la nube
        cloud_file = ai_provider_service.upload_to_cloud(video_files[0], mime_type="video/mp4")
        
        # 3. Solicitar análisis
        prompt = f"""
        Analiza este video y el guion proporcionado para extraer el contexto visual estratégico y su ADN Estético.
        
        Guion: {script_text[:1000]}
        
        Evalúa específicamente:
        1. ADN Estético: ¿Es 'Quiet Luxury' (minimalista, tonos neutros, luz suave) o 'Loud Marketing' (colores chillones, cortes rápidos, saturado)?
        2. Calidad de Producción: Iluminación, composición de encuadre y estabilidad de cámara.
        
        Responde exclusivamente en JSON con esta estructura:
        {{
          "escenario": "descripción",
          "elementos_clave": ["elemento"],
          "estilo_visual": "descripción (ej: cinemático, minimalista, vlog)",
          "estetica_dna": {{
            "vibe": "quiet_luxury|loud_marketing|neutral",
            "paleta": ["color"], 
            "iluminacion": "suave|dura|natural|artificial", 
            "framing": "close-up|medium|wide",
            "estabilidad": "alta|media|baja"
          }},
          "sugerencias_creativas": ["sugerencia"],
          "ocr_detectado": ["texto en pantalla"]
        }}
        """
        return ai_provider_service.generate_cloud_json(prompt, [cloud_file])

visual_service = VisualService()
