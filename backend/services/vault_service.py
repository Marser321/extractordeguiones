import os
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from core.config import settings
    from services.insforge_service import insforge_service
except ModuleNotFoundError:
    from backend.core.config import settings
    from backend.services.insforge_service import insforge_service

class VaultService:
    def __init__(self):
        self.root = settings.VAULT_ROOT
        self._ensure_dir(self.root)
        self.marcas_dir = self.root / "Marcas"
        self._ensure_dir(self.marcas_dir)

    def _ensure_dir(self, path: Path):
        """Asegura que el directorio exista."""
        if not path.exists():
            os.makedirs(path)

    def _safe_name(self, value: str, field_name: str) -> str:
        """Valida nombres usados como carpetas dentro del Vault."""
        clean_value = value.strip()
        if not clean_value:
            raise ValueError(f"{field_name} no puede estar vacío.")
        if not re.fullmatch(r"[\w .-]+", clean_value, re.UNICODE):
            raise ValueError(f"{field_name} solo puede contener letras, números, espacios, puntos, guiones y guiones bajos.")
        if clean_value in {".", ".."}:
            raise ValueError(f"{field_name} no es válido.")
        return clean_value

    def create_brand_structure(self, brand_name: str) -> Path:
        """Crea la estructura de carpetas para una nueva marca."""
        brand_name = self._safe_name(brand_name, "brand_name")
        brand_path = self.marcas_dir / brand_name
        self._ensure_dir(brand_path)
        
        # Subcarpetas
        self._ensure_dir(brand_path / "Analisis")
        self._ensure_dir(brand_path / "Contenido")
        
        return brand_path

    def create_video_entry(self, brand_name: str, video_id: str) -> Path:
        """Crea la carpeta para un video específico de una marca."""
        video_id = self._safe_name(video_id, "video_id")
        brand_path = self.create_brand_structure(brand_name)
        video_path = brand_path / "Contenido" / video_id
        self._ensure_dir(video_path)
        return video_path

    def create_original_video_dir(self, brand_name: str, video_id: str) -> Path:
        """Crea la carpeta donde se preservan videos subidos desde navegador."""
        video_path = self.create_video_entry(brand_name, video_id)
        original_dir = video_path / "original_video"
        self._ensure_dir(original_dir)
        return original_dir

    def create_analysis_dir(self, brand_name: str, video_id: str) -> Path:
        video_path = self.create_video_entry(brand_name, video_id)
        analysis_dir = video_path / "Analisis"
        self._ensure_dir(analysis_dir)
        return analysis_dir

    def create_frames_dir(self, brand_name: str, video_id: str) -> Path:
        video_path = self.create_video_entry(brand_name, video_id)
        frames_dir = video_path / "Frames"
        self._ensure_dir(frames_dir)
        return frames_dir

    def save_uploaded_file(self, brand_name: str, video_id: str, filename: str, source_file) -> Path:
        """Guarda un archivo subido dentro del Vault."""
        safe_filename = Path(filename or "video_upload").name
        if safe_filename in {"", ".", ".."}:
            safe_filename = "video_upload"
        original_dir = self.create_original_video_dir(brand_name, video_id)
        file_path = original_dir / safe_filename
        with open(file_path, "wb") as output:
            shutil.copyfileobj(source_file, output)
        return file_path

    def get_video_path(self, brand_name: str, video_id: str) -> Path:
        brand_name = self._safe_name(brand_name, "brand_name")
        video_id = self._safe_name(video_id, "video_id")
        return self.marcas_dir / brand_name / "Contenido" / video_id

    def save_file(self, path: Path, filename: str, content: str):
        """Guarda un archivo de texto en la ruta especificada."""
        file_path = path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def save_json(self, path: Path, filename: str, data: dict):
        """Guarda un archivo JSON en la ruta especificada."""
        file_path = path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return file_path

    def read_file(self, path: Path) -> Optional[str]:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def read_json(self, path: Path) -> Optional[dict]:
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def default_brand_profile(self, brand_name: str) -> dict:
        return {
            "brand_name": brand_name,
            "tone": "claro, experto, directo y accionable",
            "audience": "audiencia interesada en contenido, marketing y crecimiento",
            "offer": "",
            "visual_style": "limpio, moderno, con foco en la idea principal",
            "colors": [],
            "forbidden_words": [],
            "cta": "Guardar, compartir o solicitar más información",
            "preferred_formats": ["reel", "short", "ad", "post"],
        }

    def get_brand_profile(self, brand_name: str) -> dict:
        # Intentar desde InsForge
        ins_profile = insforge_service.get_brand_profile(brand_name)
        if ins_profile:
            # Sync localmente
            brand_path = self.create_brand_structure(brand_name)
            self.save_json(brand_path, "brand_profile.json", ins_profile)
            return ins_profile

        # Fallback local
        brand_path = self.create_brand_structure(brand_name)
        profile_path = brand_path / "brand_profile.json"
        profile = self.read_json(profile_path)
        if profile:
            # Sync con InsForge
            insforge_service.create_or_update_brand(profile)
            return profile
            
        profile = self.default_brand_profile(brand_name)
        self.save_json(brand_path, "brand_profile.json", profile)
        insforge_service.create_or_update_brand(profile)
        return profile

    def save_brand_profile(self, brand_name: str, profile: dict) -> dict:
        brand_path = self.create_brand_structure(brand_name)
        current = self.get_brand_profile(brand_name)
        merged = {**current, **profile, "brand_name": brand_name, "name": brand_name}
        self.save_json(brand_path, "brand_profile.json", merged)
        # Sync con InsForge
        insforge_service.create_or_update_brand(merged)
        return merged

    def update_brand_patterns(
        self,
        brand_name: str,
        additions: dict,
        source_video_id: Optional[str] = None,
        prompt_version: Optional[str] = None,
        audit_score: Optional[float] = None,
        promote: bool = True,
        promotion_threshold: float = 7.0,
    ) -> dict:
        brand_path = self.create_brand_structure(brand_name)
        patterns_path = brand_path / "Analisis" / "patrones.json"
        current: dict[str, Any] = self.read_json(patterns_path) or {
            "hooks_frecuentes": [],
            "estructuras_ganadoras": [],
            "angulos_de_venta": [],
            "reglas_de_estilo": [],
        }
        current.setdefault("pattern_candidates", [])
        current.setdefault("pattern_metadata", [])
        can_promote = promote and (audit_score is None or audit_score >= promotion_threshold)
        observed_at = datetime.utcnow().isoformat() + "Z"

        for key, values in additions.items():
            if not isinstance(values, list):
                continue
            for value in values:
                if not value:
                    continue
                candidate = {
                    "category": key,
                    "value": value,
                    "source_video_id": source_video_id,
                    "prompt_version": prompt_version,
                    "audit_score": audit_score,
                    "promoted": can_promote,
                    "observed_at": observed_at,
                }
                duplicate_candidate = any(
                    item.get("category") == key
                    and item.get("value") == value
                    and item.get("source_video_id") == source_video_id
                    for item in current["pattern_candidates"]
                )
                if not duplicate_candidate:
                    current["pattern_candidates"].append(candidate)
                if can_promote:
                    existing = current.setdefault(key, [])
                    if value not in existing:
                        existing.append(value)
                    duplicate_metadata = any(
                        item.get("category") == key
                        and item.get("value") == value
                        and item.get("source_video_id") == source_video_id
                        for item in current["pattern_metadata"]
                    )
                    if not duplicate_metadata:
                        current["pattern_metadata"].append(candidate)

        for key in ("hooks_frecuentes", "estructuras_ganadoras", "angulos_de_venta", "reglas_de_estilo"):
            values = current.get(key)
            if isinstance(values, list):
                current[key] = values[-40:]
        current["pattern_candidates"] = current["pattern_candidates"][-120:]
        current["pattern_metadata"] = current["pattern_metadata"][-120:]
        self.save_json(brand_path / "Analisis", "patrones.json", current)
        return current

    def list_brands(self) -> list:
        # Combinar local y base de datos
        local_brands = []
        if self.marcas_dir.exists():
            for brand_path in sorted(self.marcas_dir.iterdir()):
                if not brand_path.is_dir():
                    continue
                videos_path = brand_path / "Contenido"
                video_count = len([path for path in videos_path.iterdir() if path.is_dir()]) if videos_path.exists() else 0
                local_brands.append({
                    "brand_name": brand_path.name,
                    "video_count": video_count,
                })
        
        ins_brands = insforge_service.list_all_brands()
        # Merge por nombre
        brands_map = {b["brand_name"]: b for b in local_brands}
        for ib in ins_brands:
            name = ib.get("name") or ib.get("brand_name")
            if name not in brands_map:
                brands_map[name] = {"brand_name": name, "video_count": 0}
            else:
                # Si está en ambos, podríamos actualizar datos del perfil si quisiéramos
                pass
        
        return sorted(brands_map.values(), key=lambda x: x["brand_name"])

    def list_videos(self, brand_name: str) -> list:
        brand_name = self._safe_name(brand_name, "brand_name")
        videos_path = self.marcas_dir / brand_name / "Contenido"
        if not videos_path.exists():
            return []
        videos = []
        for video_path in sorted(videos_path.iterdir()):
            if video_path.is_dir():
                videos.append(self.describe_video(brand_name, video_path.name))
        return videos

    def describe_video(self, brand_name: str, video_id: str) -> dict:
        video_path = self.get_video_path(brand_name, video_id)
        transcription = self.read_json(video_path / "metadatos_transcripcion.json") or {}
        source = self.read_json(video_path / "source_metadata.json") or {}
        analysis = self.read_json(video_path / "analisis_estado.json") or {}
        pro_analysis = self.read_json(video_path / "Analisis" / "analisis_estado.json") or {}
        if pro_analysis:
            analysis = pro_analysis
        files = {}
        expected_files = {
            "audio": "audio_extract.wav",
            "script": "guion_original.txt",
            "metadata": "metadatos_transcripcion.json",
            "source_metadata": "source_metadata.json",
        }
        for key, filename in expected_files.items():
            file_path = video_path / filename
            if file_path.exists():
                files[key] = str(file_path)

        analysis_outputs = self.list_outputs(brand_name, video_id)
        for output in analysis_outputs:
            files[output["key"]] = output["path"]

        original_dir = video_path / "original_video"
        original_files = [str(path) for path in sorted(original_dir.iterdir()) if path.is_file()] if original_dir.exists() else []
        
        frames_dir = video_path / "Frames"
        frames = [f.name for f in sorted(frames_dir.glob("*.jpg"))] if frames_dir.exists() else []
        creative_dir = video_path / "Analisis" / "CreativeLab"
        creative_pack = self.read_json(creative_dir / "creative_pack.json") or {}

        created_at = None
        if video_path.exists():
            created_at = video_path.stat().st_mtime

        return {
            "brand_name": brand_name,
            "video_id": video_id,
            "path": str(video_path),
            "created_at": created_at,
            "source_type": source.get("source_type"),
            "source_value": source.get("source_value"),
            "language": transcription.get("language_detected"),
            "segments_count": len(transcription.get("segments", [])),
            "status": "completed" if (video_path / "guion_original.txt").exists() else "pending",
            "analysis_status": analysis.get("status", "missing"),
            "audit": self.read_json(video_path / "Analisis" / "auditoria_contexto.json") or {},
            "creative_pack": {
                "available": bool(creative_pack),
                "metadata": creative_pack.get("pack_metadata", {}) if isinstance(creative_pack, dict) else {},
                "json_path": str(creative_dir / "creative_pack.json") if (creative_dir / "creative_pack.json").exists() else None,
                "markdown_path": str(creative_dir / "creative_pack.md") if (creative_dir / "creative_pack.md").exists() else None,
            },
            "files": files,
            "outputs": analysis_outputs,
            "original_files": original_files,
            "frames": frames,
        }

    def list_outputs(self, brand_name: str, video_id: str) -> list:
        video_path = self.get_video_path(brand_name, video_id)
        analysis_dir = video_path / "Analisis"
        if not analysis_dir.exists():
            return []
        labels = {
            "analisis_estado.json": ("analysis_status", "Estado"),
            "auditoria_contexto.json": ("context_audit", "Auditoría contexto"),
            "resumen_ejecutivo.md": ("summary", "Resumen"),
            "hooks.json": ("hooks", "Hooks"),
            "momentos_virales.json": ("viral_moments", "Momentos virales"),
            "estructura_narrativa.json": ("narrative_structure", "Estructura narrativa"),
            "ideas_reels.json": ("reel_ideas", "Ideas de reels"),
            "ads.json": ("ads", "Ads"),
            "brief_creativo.md": ("creative_brief", "Brief creativo"),
            "captions.json": ("captions", "Captions"),
            "calendario_publicacion.json": ("calendar", "Calendario"),
            "prompts_visuales.json": ("visual_prompts", "Prompts visuales"),
            "prompt_base_marca.json": ("brand_prompt", "Prompt base"),
            "analisis_visual.json": ("visual_analysis", "Análisis visual"),
            "retrospectiva.json": ("retrospective", "Retrospectiva"),
        }
        outputs = []
        for filename, (key, label) in labels.items():
            file_path = analysis_dir / filename
            if file_path.exists():
                outputs.append({
                    "key": key,
                    "label": label,
                    "filename": filename,
                    "path": str(file_path),
                })
        creative_outputs = {
            "creative_pack.json": ("creative_pack_json", "Creative pack JSON"),
            "creative_pack.md": ("creative_pack_md", "Creative pack Markdown"),
        }
        creative_dir = analysis_dir / "CreativeLab"
        for filename, (key, label) in creative_outputs.items():
            file_path = creative_dir / filename
            if file_path.exists():
                outputs.append({
                    "key": key,
                    "label": label,
                    "filename": filename,
                    "path": str(file_path),
                })
        return outputs

vault_service = VaultService()
