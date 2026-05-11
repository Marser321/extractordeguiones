import subprocess
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import yt_dlp
try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg = None

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings


INSTAGRAM_CLOUD_MESSAGE = (
    "Instagram bloquea con frecuencia las descargas anónimas desde Vercel por login, cookies o rate-limit. "
    "Para procesar este reel/video en la app desplegada, descárgalo en tu dispositivo y usa la opción "
    "'Arrastra video'."
)


class MediaService:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffmpeg_available = self.ffmpeg_path is not None

    def _find_ffmpeg(self) -> Optional[str]:
        # 1. Intentar con el PATH del sistema
        binary = shutil.which("ffmpeg")
        if binary:
            return binary
        
        # 2. Intentar con imageio-ffmpeg (ideal para Vercel)
        if imageio_ffmpeg:
            try:
                path = imageio_ffmpeg.get_ffmpeg_exe()
                if path:
                    return path
            except Exception:
                pass
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
            if not self.ffmpeg_path:
                raise RuntimeError("FFmpeg no está instalado. En Vercel, asegúrate de que imageio-ffmpeg esté en requirements.txt.")
            self.ffmpeg_available = True

    def _is_instagram_url(self, url: str) -> bool:
        hostname = urlparse(url).hostname or ""
        return hostname.lower().removeprefix("www.") in {"instagram.com", "instagr.am"}

    def validate_url_source(self, url: str):
        if settings.IS_CLOUD and self._is_instagram_url(url):
            raise ValueError(INSTAGRAM_CLOUD_MESSAGE)

    def _is_cloud_download_block(self, error_msg: str) -> bool:
        text = error_msg.lower()
        markers = (
            "video unavailable",
            "403",
            "requested content is not available",
            "rate-limit",
            "rate limit",
            "login required",
            "cookies",
            "instagram",
            "sign in to confirm",
            "not a bot",
        )
        return any(marker in text for marker in markers)

    def process_url(self, url: str, output_path: Path) -> Path:
        """
        Descarga el audio de una URL (YouTube, Instagram, etc) y lo guarda en formato WAV a 16kHz
        ideal para Whisper.
        """
        self.validate_url_source(url)
        self._ensure_ffmpeg()
        audio_filename = "audio_extract.wav"
        final_path = output_path / audio_filename
        
        # Opciones de yt-dlp para extraer mejor calidad de audio compatible con whisper
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(final_path).replace('.wav', ''), # yt-dlp añade la extensión
            'ffmpeg_location': self.ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'postprocessor_args': [
                '-ar', '16000', # 16 kHz sample rate (ideal para whisper)
                '-ac', '1'      # Mono
            ],
            'quiet': True,
            'no_warnings': True,
            'player_client': ['android', 'ios'],
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                    'player_skip': ['webpage', 'configs'],
                    'include_dash_manifest': [False],
                    'include_hls_manifest': [False],
                }
            },
            'noproxy': True,
            'check_formats': False,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'referer': 'https://www.youtube.com/',
            'geo_bypass': True,
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            error_msg = str(e)
            if settings.IS_CLOUD and self._is_cloud_download_block(error_msg):
                if self._is_instagram_url(url):
                    raise RuntimeError(INSTAGRAM_CLOUD_MESSAGE) from e
                raise RuntimeError(
                    "La descarga por URL fue bloqueada desde Vercel por el origen del video. "
                    "Descarga el archivo y súbelo con la opción 'Arrastra video', o prueba con un link público directo."
                ) from e
            raise Exception(f"Error al descargar contenido de la URL: {error_msg}")
            
        return final_path

    def download_video(self, url: str, output_path: Path) -> Path:
        """
        Descarga el video original de una URL.
        """
        # Crear carpeta para el video original si no existe
        original_dir = output_path / "original_video"
        original_dir.mkdir(parents=True, exist_ok=True)
        
        video_filename = "video_original.mp4"
        final_path = original_dir / video_filename
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(final_path),
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                    'player_skip': ['webpage', 'configs']
                }
            },
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'referer': 'https://www.youtube.com/',
            'geo_bypass': True,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        return final_path

    def process_local_file(self, file_path: Path, output_path: Path) -> Path:
        """
        Extrae el audio de un archivo de video local y lo convierte a WAV 16kHz mono.
        """
        self._ensure_ffmpeg()
        if not file_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo local: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"La ruta local no apunta a un archivo: {file_path}")

        audio_filename = "audio_extract.wav"
        final_path = output_path / audio_filename
        
        command = [
            self.ffmpeg_path,
            "-i", str(file_path),
            "-vn", # No video
            "-acodec", "pcm_s16le", # PCM 16-bit
            "-ar", "16000", # 16 kHz
            "-ac", "1", # Mono
            "-y", # Sobrescribir si existe
            str(final_path)
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error procesando video local con ffmpeg: {e.stderr.decode()}")
            
        return final_path

media_service = MediaService()
