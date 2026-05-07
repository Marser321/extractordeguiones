import subprocess
from pathlib import Path
import yt_dlp

class MediaService:
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _ensure_ffmpeg(self):
        if not self.ffmpeg_available and not self._check_ffmpeg():
            raise RuntimeError("FFmpeg no está instalado o no se encuentra en el PATH. Es requerido para el procesamiento de audio.")
        self.ffmpeg_available = True

    def process_url(self, url: str, output_path: Path) -> Path:
        """
        Descarga el audio de una URL (YouTube, Instagram, etc) y lo guarda en formato WAV a 16kHz
        ideal para Whisper.
        """
        self._ensure_ffmpeg()
        audio_filename = "audio_extract.wav"
        final_path = output_path / audio_filename
        
        # Opciones de yt-dlp para extraer mejor calidad de audio compatible con whisper
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(final_path).replace('.wav', ''), # yt-dlp añade la extensión
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'postprocessor_args': [
                '-ar', '16000', # 16 kHz sample rate (ideal para whisper)
                '-ac', '1'      # Mono
            ],
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
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
            'no_warnings': True
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
            "ffmpeg",
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
