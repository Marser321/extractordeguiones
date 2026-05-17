from concurrent.futures import ThreadPoolExecutor
import base64
from datetime import datetime
import json
from pathlib import Path
from threading import Lock
from typing import Callable, Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, model_validator

try:
    from core.config import settings
    from services.analysis_service import analysis_service
    from services.ai_provider_service import ai_provider_service
    from services.context_audit_service import context_audit_service
    from services.creative_pack_service import creative_pack_service
    from services.llm_service import llm_service
    from services.media_service import media_service
    from services.microtask_service import microtask_service
    from services.ollama_control_service import ollama_control_service
    from services.transcription_service import transcription_service
    from services.vault_service import vault_service
    from services.visual_service import visual_service
    from services.insforge_service import insforge_service
    from services.brand_shifting_service import brand_shifting_service
except ModuleNotFoundError:
    from backend.core.config import settings
    from backend.services.analysis_service import analysis_service
    from backend.services.ai_provider_service import ai_provider_service
    from backend.services.context_audit_service import context_audit_service
    from backend.services.creative_pack_service import creative_pack_service
    from backend.services.llm_service import llm_service
    from backend.services.media_service import media_service
    from backend.services.microtask_service import microtask_service
    from backend.services.ollama_control_service import ollama_control_service
    from backend.services.transcription_service import transcription_service
    from backend.services.vault_service import vault_service
    from backend.services.visual_service import visual_service
    from backend.services.insforge_service import insforge_service
    from backend.services.brand_shifting_service import brand_shifting_service


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
JOB_STEPS = {
    "queued": 5,
    "extracting_audio": 25,
    "transcribing": 62,
    "analyzing": 74,
    "analyzing_text": 78,
    "extracting_frames": 86,
    "analyzing_visuals": 90,
    "generating_assets": 94,
    "completed": 100,
    "failed": 100,
}

app = FastAPI(title="ScriptDNA Orchestrator API")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

executor = ThreadPoolExecutor(max_workers=2)
jobs_lock = Lock()
jobs = {}


class PromptRequest(BaseModel):
    prompt: str
    engine: Literal["ollama", "gemini-flash", "gemini-pro"] = "gemini-flash"
    model: Optional[str] = None


class VaultCreateRequest(BaseModel):
    brand_name: str
    video_id: str


class MediaExtractRequest(BaseModel):
    brand_name: str
    video_id: str
    url: Optional[str] = None
    local_file_path: Optional[str] = None

    @model_validator(mode="after")
    def require_media_source(self):
        if not self.url and not self.local_file_path:
            raise ValueError("Se requiere una URL o un local_file_path.")
        return self


class TranscribeRequest(BaseModel):
    brand_name: str
    video_id: str
    audio_filename: str = "audio_extract.wav"


class PipelineProcessRequest(MediaExtractRequest):
    pass

class AdaptScriptRequest(BaseModel):
    original_script: str
    target_brand: str


class JobUrlRequest(BaseModel):
    brand_name: str
    video_id: str
    url: str
    ai_provider: str = settings.AI_DEFAULT_PROVIDER
    ai_model: Optional[str] = None
    analysis_modules: Optional[list] = None


class JobLocalPathRequest(BaseModel):
    brand_name: str
    video_id: str
    local_file_path: str
    ai_provider: str = settings.AI_DEFAULT_PROVIDER
    ai_model: Optional[str] = None
    analysis_modules: Optional[list] = None


class JobProcessRequest(BaseModel):
    brand_name: str
    video_id: str
    url: Optional[str] = None
    local_file_path: Optional[str] = None
    ai_provider: str = settings.AI_DEFAULT_PROVIDER
    ai_model: Optional[str] = None
    analysis_modules: Optional[list] = None

    @model_validator(mode="after")
    def require_media_source(self):
        if not self.url and not self.local_file_path:
            raise ValueError("Se requiere una URL o un local_file_path.")
        if self.url and self.local_file_path:
            raise ValueError("Usa solo una fuente por job: url o local_file_path.")
        return self


class AITestRequest(BaseModel):
    provider: str = settings.AI_DEFAULT_PROVIDER
    model: Optional[str] = None
    prompt: str = "Responde en JSON: {\"ok\": true, \"message\": \"ScriptDNA conectado\"}"


class BrandProfileRequest(BaseModel):
    tone: Optional[str] = None
    audience: Optional[str] = None
    offer: Optional[str] = None
    visual_style: Optional[str] = None
    colors: Optional[list] = None
    forbidden_words: Optional[list] = None
    cta: Optional[str] = None
    preferred_formats: Optional[list] = None


class AnalyzeJobRequest(BaseModel):
    ai_provider: str = settings.AI_DEFAULT_PROVIDER
    ai_model: Optional[str] = None
    analysis_modules: Optional[list] = None


class CreativePackRequest(BaseModel):
    ai_provider: str = settings.AI_DEFAULT_PROVIDER
    ai_model: Optional[str] = None
    fallback_provider: Optional[str] = None


class MicrotaskRunRequest(BaseModel):
    groups: Optional[list[str]] = None


class RefineJobRequest(BaseModel):
    ai_provider: str = settings.AI_DEFAULT_PROVIDER
    ai_model: Optional[str] = None


class GenerateImageRequest(BaseModel):
    prompt: str
    brand_name: str
    video_id: str
    provider: str = settings.IMAGE_DEFAULT_PROVIDER
    model: Optional[str] = None
    size: str = "1024x1024"


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _preview(text: str, size: int = 700) -> str:
    if len(text) <= size:
        return text
    return text[:size].rstrip() + "..."


def _public_job(job_id: str) -> dict:
    with jobs_lock:
        return dict(jobs[job_id])


def _job_snapshot(job_id: str) -> Optional[dict]:
    with jobs_lock:
        job = jobs.get(job_id)
        return dict(job) if job else None


def _record_to_job(record: Optional[dict]) -> Optional[dict]:
    if not record:
        return None
    state = {}
    raw_state = record.get("analyzed_script")
    if isinstance(raw_state, str) and raw_state:
        try:
            parsed = json.loads(raw_state)
            state = parsed.get("job_state", parsed) if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            state = {}
    elif isinstance(raw_state, dict):
        state = raw_state.get("job_state", raw_state)

    result = state.get("result")
    if result is None and record.get("creative_prompts"):
        result = record.get("creative_prompts")

    return {
        "job_id": record.get("job_id") or state.get("job_id"),
        "status": record.get("status") or state.get("status") or "pending",
        "progress": state.get("progress", JOB_STEPS.get(record.get("status"), 0)),
        "message": state.get("message") or "Estado recuperado desde InsForge.",
        "brand_name": record.get("brand_name") or state.get("brand_name"),
        "video_id": record.get("video_id_str") or state.get("video_id"),
        "source_type": state.get("source_type"),
        "source_value": record.get("video_url") or state.get("source_value"),
        "ai_provider": state.get("ai_provider"),
        "ai_model": state.get("ai_model"),
        "analysis_modules": state.get("analysis_modules") or [],
        "created_at": state.get("created_at"),
        "updated_at": state.get("updated_at"),
        "error": state.get("error"),
        "result": result,
        "insforge_id": record.get("id"),
    }


def _public_job_from_cache_or_store(job_id: str) -> Optional[dict]:
    cached = _job_snapshot(job_id)
    if cached:
        return cached
    return _record_to_job(insforge_service.get_video_script_by_job_id(job_id))


def _read_text_if_exists(path: Path) -> Optional[str]:
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def _read_json_if_exists(path: Path):
    if path.exists() and path.is_file():
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return None


def _collect_output_payload(brand_name: str, video_id: str) -> dict:
    video_path = vault_service.get_video_path(brand_name, video_id)
    analysis_dir = video_path / "Analisis"
    creative_dir = analysis_dir / "CreativeLab"
    payload = {
        "script": _read_text_if_exists(video_path / "guion_original.txt"),
        "metadata": _read_json_if_exists(video_path / "metadatos_transcripcion.json"),
        "source_metadata": _read_json_if_exists(video_path / "source_metadata.json"),
        "analysis": {},
        "creative_pack": {
            "json": _read_json_if_exists(creative_dir / "creative_pack.json"),
            "markdown": _read_text_if_exists(creative_dir / "creative_pack.md"),
        },
    }
    for output in vault_service.list_outputs(brand_name, video_id):
        filename = output.get("filename")
        path = Path(output.get("path", ""))
        if not filename or not path.exists() or filename in {"creative_pack.json", "creative_pack.md"}:
            continue
        if filename.endswith(".json"):
            payload["analysis"][filename] = _read_json_if_exists(path)
        else:
            payload["analysis"][filename] = _read_text_if_exists(path)
    return payload


def _stored_output_payload(brand_name: str, video_id: str) -> dict:
    record = insforge_service.get_video_script(brand_name, video_id)
    if not record:
        return {}
    job = _record_to_job(record) or {}
    result = job.get("result") or {}
    if isinstance(result, dict):
        return result.get("output_payload") or result.get("outputs_payload") or {}
    return {}


def _active_ollama_jobs() -> list[dict]:
    active_statuses = {"queued", "extracting_audio", "transcribing", "analyzing", "analyzing_text", "extracting_frames", "analyzing_visuals", "generating_assets"}
    with jobs_lock:
        return [
            dict(job)
            for job in jobs.values()
            if job.get("ai_provider") == "ollama" and job.get("status") in active_statuses
        ]


def _ensure_ai_provider_available(ai_provider: str):
    if ai_provider == "ollama":
        if settings.IS_CLOUD:
            raise HTTPException(
                status_code=400,
                detail="Ollama solo está disponible en modo local/desarrollo. Usa Qwen API para el despliegue cloud.",
            )
        status = ollama_control_service.status()
        if not status["running"]:
            raise HTTPException(
                status_code=400,
                detail="Ollama está apagado. Enciéndelo desde la pestaña IA o selecciona Qwen API para este job.",
            )
    elif ai_provider == "qwen":
        status = ai_provider_service.status()
        if not status["qwen"]["available"]:
            raise HTTPException(
                status_code=400,
                detail="Qwen/DashScope no está configurado. Configura DASHSCOPE_API_KEY o QWEN_API_KEY en .env.",
            )
    elif ai_provider == "huggingface":
        status = ai_provider_service.status()
        if not status["huggingface"]["available"]:
            raise HTTPException(
                status_code=400,
                detail="Hugging Face no está configurado. Configura HF_TOKEN en .env.",
            )
    elif ai_provider == "fal":
        raise HTTPException(
            status_code=400,
            detail="fal se usa para imagen/video, no para análisis de texto. Usa Qwen API como motor principal.",
        )
    elif ai_provider == "gemini":
        status = ai_provider_service.status()
        if not status["gemini"]["available"]:
            raise HTTPException(
                status_code=400,
                detail="Gemini no está configurado o no tiene SDK disponible. Configura GEMINI_API_KEY en .env o usa Qwen.",
            )
    elif ai_provider == "openrouter":
        status = ai_provider_service.status()
        if not status["openrouter"]["available"]:
            raise HTTPException(
                status_code=400,
                detail="OpenRouter no está configurado (falta llave API).",
            )
    elif ai_provider == "groq":
        status = ai_provider_service.status()
        if not status["groq"]["available"]:
            raise HTTPException(
                status_code=400,
                detail="Groq no está configurado (falta llave API).",
            )
    else:
        raise HTTPException(status_code=400, detail=f"Proveedor IA no soportado: {ai_provider}")


def _create_job(
    brand_name: str,
    video_id: str,
    source_type: str,
    source_value: str,
    ai_provider: str = settings.AI_DEFAULT_PROVIDER,
    ai_model: Optional[str] = None,
    analysis_modules: Optional[list] = None,
) -> str:
    job_id = uuid4().hex
    now = _now()
    initial_state = {
        "job_id": job_id,
        "status": "queued",
        "progress": JOB_STEPS["queued"],
        "message": "Trabajo creado.",
        "brand_name": brand_name,
        "video_id": video_id,
        "source_type": source_type,
        "source_value": source_value,
        "ai_provider": ai_provider,
        "ai_model": ai_model,
        "analysis_modules": analysis_modules or analysis_service.default_modules(),
        "created_at": now,
        "updated_at": now,
        "error": None,
        "result": None,
        "insforge_id": None,
    }
    with jobs_lock:
        jobs[job_id] = initial_state
    
    # Persistir en InsForge
    ins_record = insforge_service.create_video_script(
        brand_name,
        video_id,
        source_value,
        job_id,
        status="queued",
        job_state=initial_state,
    )
    if ins_record:
        with jobs_lock:
            jobs[job_id]["insforge_id"] = ins_record["id"]
            
    return job_id


def _update_job(job_id: str, status: str, message: str, result: Optional[dict] = None, error: Optional[str] = None):
    with jobs_lock:
        job = jobs[job_id]
        job["status"] = status
        job["progress"] = JOB_STEPS.get(status, job.get("progress", 0))
        job["message"] = message
        job["updated_at"] = _now()
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error
        snapshot = dict(job)
            
    # Sync con InsForge
    with jobs_lock:
        job = jobs[job_id]
        ins_id = job.get("insforge_id")
    
    updates = {
        "status": "failed" if error else status,
        "analyzed_script": json.dumps({"job_state": snapshot}, ensure_ascii=False),
    }
    if result:
        updates["original_script"] = result.get("script_preview")
        updates["creative_prompts"] = result
        if "segments_count" in result:
            updates["video_url"] = result.get("video_url") or job.get("source_value")

    if ins_id:
        insforge_service.update_video_script(ins_id, updates)
    else:
        insforge_service.update_video_script_by_job_id(job_id, updates)


def _run_media_extract(request: MediaExtractRequest) -> tuple:
    video_path = vault_service.create_video_entry(request.brand_name, request.video_id)

    if request.url:
        audio_file = media_service.process_url(request.url, video_path)
        source_type = "url"
        source_value = request.url
    else:
        local_path = Path(request.local_file_path).expanduser()
        audio_file = media_service.process_local_file(local_path, video_path)
        source_type = "local_file"
        source_value = str(local_path)

    vault_service.save_json(video_path, "source_metadata.json", {
        "source_type": source_type,
        "source_value": source_value,
        "processed_at": _now(),
    })
    return video_path, source_type, audio_file


def _run_transcription(video_path: Path, audio_filename: str = "audio_extract.wav") -> tuple:
    audio_path = video_path / audio_filename
    if not audio_path.exists():
        raise FileNotFoundError(f"No se encontró el audio en {audio_path}")

    result = transcription_service.transcribe_audio(audio_path, language="es")
    script_path = vault_service.save_file(video_path, "guion_original.txt", result["full_text"])
    metadata_path = vault_service.save_json(video_path, "metadatos_transcripcion.json", result)
    return result, script_path, metadata_path


def _build_result(
    brand_name: str,
    video_id: str,
    source_type: str,
    video_path: Path,
    audio_file: Path,
    transcription: dict,
    script_path: Path,
    metadata_path: Path,
    analysis_status: Optional[dict] = None,
) -> dict:
    return {
        "status": "completed",
        "message": "Audio extraído y transcripción completada",
        "brand_name": brand_name,
        "video_id": video_id,
        "source_type": source_type,
        "vault_path": str(video_path),
        "audio_path": str(audio_file),
        "script_path": str(script_path),
        "metadata_path": str(metadata_path),
        "analysis_status": analysis_status or {},
        "outputs": vault_service.list_outputs(brand_name, video_id),
        "language": transcription["language_detected"],
        "language_probability": transcription["language_probability"],
        "segments_count": len(transcription["segments"]),
        "script_preview": _preview(transcription["full_text"]),
    }


def _run_analysis(video_path: Path, brand_name: str, video_id: str, ai_provider: str, ai_model: Optional[str], analysis_modules: Optional[list]) -> dict:
    script_path = video_path / "guion_original.txt"
    script_text = vault_service.read_file(script_path)
    if not script_text:
        raise FileNotFoundError(f"No se encontró guion para analizar en {script_path}")
    return analysis_service.analyze_script(
        video_path=video_path,
        brand_name=brand_name,
        video_id=video_id,
        script_text=script_text,
        ai_provider=ai_provider,
        ai_model=ai_model,
        analysis_modules=analysis_modules,
    )


def _process_job(
    job_id: str,
    brand_name: str,
    video_id: str,
    source_type: str,
    media_runner: Callable[[Path], Path],
    ai_provider: str,
    ai_model: Optional[str],
    analysis_modules: Optional[list],
):
    try:
        video_path = vault_service.create_video_entry(brand_name, video_id)
        _update_job(job_id, "extracting_audio", "Extrayendo audio.")
        audio_file = media_runner(video_path)

        _update_job(job_id, "transcribing", "Transcribiendo audio.")
        transcription, script_path, metadata_path = _run_transcription(video_path)

        # MT-02: Extracción Visual
        try:
            video_source = None
            if source_type == "local_path":
                video_source = Path(jobs[job_id]["source_value"])
            elif source_type == "upload":
                original_dir = video_path / "original_video"
                files = list(original_dir.iterdir()) if original_dir.exists() else []
                video_source = files[0] if files else None
            
            if video_source and video_source.exists():
                _update_job(job_id, "extracting_frames", "Extrayendo frames del video.")
                visual_service.extract_frames(video_source, brand_name, video_id)

                # MT-03: Análisis Visual
                if ai_provider in {"qwen", "gemini"}:
                    label = "Qwen Vision" if ai_provider == "qwen" else "Gemini Vision"
                    _update_job(job_id, "analyzing_visuals", f"Analizando contexto visual con {label}.")
                    visual_analysis = visual_service.analyze_frames(brand_name, video_id, transcription["full_text"], provider=ai_provider)
                    # Guardar el análisis visual en el vault
                    analysis_dir = vault_service.create_analysis_dir(brand_name, video_id)
                    vault_service.save_json(analysis_dir, "analisis_visual.json", visual_analysis)
        except Exception as ve:
            print(f"[Visual] Error omitido en extracción/análisis visual: {ve}")

        _update_job(job_id, "analyzing_text", "Analizando guion con IA.")
        analysis_status = analysis_service.analyze_script(
            video_path,
            brand_name,
            video_id,
            transcription["full_text"],
            ai_provider=ai_provider,
            ai_model=ai_model,
            analysis_modules=analysis_modules,
        )

        result = _build_result(
            brand_name,
            video_id,
            source_type,
            video_path,
            audio_file,
            transcription,
            script_path,
            metadata_path,
            analysis_status,
        )
        result["output_payload"] = _collect_output_payload(brand_name, video_id)
        _update_job(job_id, "completed", "Trabajo completado.", result=result)
    except Exception as error:
        _update_job(job_id, "failed", "El trabajo falló.", error=str(error))


def _process_analysis_job(
    job_id: str,
    brand_name: str,
    video_id: str,
    ai_provider: str,
    ai_model: Optional[str],
    analysis_modules: Optional[list],
):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        if not video_path.exists():
            raise FileNotFoundError("Video no encontrado en el Vault.")
        _update_job(job_id, "analyzing_text", "Analizando guion existente con IA.")
        analysis_status = _run_analysis(video_path, brand_name, video_id, ai_provider, ai_model, analysis_modules)
        result = {
            "status": "completed",
            "message": "Análisis completado",
            "brand_name": brand_name,
            "video_id": video_id,
            "vault_path": str(video_path),
            "analysis_status": analysis_status,
            "outputs": vault_service.list_outputs(brand_name, video_id),
        }
        result["output_payload"] = _collect_output_payload(brand_name, video_id)
        _update_job(job_id, "completed", "Análisis completado.", result=result)
        print(f"[Analysis] Job {job_id} completed successfully for {brand_name}/{video_id}")
    except Exception as error:
        print(f"[Analysis] Job {job_id} failed: {error}")
        _update_job(job_id, "failed", "El análisis falló.", error=str(error))


def _process_creative_pack_job(
    job_id: str,
    brand_name: str,
    video_id: str,
    ai_provider: str,
    ai_model: Optional[str],
    fallback_provider: Optional[str],
):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        if not video_path.exists():
            raise FileNotFoundError("Video no encontrado en el Vault.")
        _update_job(job_id, "generating_assets", "Generando laboratorio creativo.")
        pack = creative_pack_service.generate_pack(
            brand_name=brand_name,
            video_id=video_id,
            ai_provider=ai_provider,
            ai_model=ai_model,
            fallback_provider=fallback_provider,
        )
        paths = creative_pack_service.pack_paths(brand_name, video_id)
        result = {
            "status": "completed",
            "message": "Creative pack generado",
            "brand_name": brand_name,
            "video_id": video_id,
            "pack_metadata": pack.get("pack_metadata", {}),
            "files": {
                "json": str(paths["json"]) if paths["json"].exists() else None,
                "markdown": str(paths["markdown"]) if paths["markdown"].exists() else None,
            },
            "outputs": vault_service.list_outputs(brand_name, video_id),
        }
        result["output_payload"] = _collect_output_payload(brand_name, video_id)
        _update_job(job_id, "completed", "Creative pack generado.", result=result)
        print(f"[CreativePack] Job {job_id} completed successfully for {brand_name}/{video_id}")
    except Exception as error:
        print(f"[CreativePack] Job {job_id} failed: {error}")
        _update_job(job_id, "failed", "El laboratorio creativo falló.", error=str(error))


def _process_refine_job(
    job_id: str,
    brand_name: str,
    video_id: str,
    ai_provider: str,
    ai_model: Optional[str]
):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        analysis_dir = vault_service.create_analysis_dir(brand_name, video_id)
        
        # Leer auditoría anterior para obtener instrucciones de refinamiento
        audit = vault_service.read_json(analysis_dir / "auditoria_contexto.json")
        if not audit or not audit.get("refinement_instructions"):
            # Si no hay auditoría previa, hacemos una nueva antes de refinar
            audit = context_audit_service.audit_video(brand_name, video_id)
            
        instructions = audit.get("refinement_instructions") or "Mejora la especificidad y fidelidad del análisis."
        
        # Leer guion y análisis anterior
        script_text = vault_service.read_file(video_path / "guion_original.txt")
        original_analysis = vault_service.read_json(analysis_dir / "full_analysis.json")
        brand_profile = vault_service.get_brand_profile(brand_name)
        patterns = vault_service.read_json(video_path.parent.parent / "Analisis" / "patrones.json") or {}
        visual_context = vault_service.read_json(analysis_dir / "analisis_visual.json") or {}
        
        # Re-construir el prompt original para pasarlo al refinador
        original_prompt = analysis_service._build_business_prompt(
            brand_name, video_id, script_text, brand_profile, 
            analysis_service.default_modules(), patterns, visual_context
        )
        
        _update_job(job_id, "analyzing_text", "Refinando análisis para mayor calidad.")
        
        refined_analysis = analysis_service.refine_analysis(
            original_analysis, instructions, original_prompt,
            ai_provider, ai_model, settings.AI_FALLBACK_PROVIDER
        )
        
        # Guardar resultados
        vault_service.save_json(analysis_dir, "full_analysis.json", refined_analysis)
        analysis_service._write_outputs(analysis_dir, refined_analysis)
        
        # Nueva auditoría post-refinamiento
        new_audit = context_audit_service.audit_video(brand_name, video_id, save=True)
        
        result = {
            "status": "completed",
            "message": "Refinamiento completado",
            "brand_name": brand_name,
            "video_id": video_id,
            "audit_score": new_audit.get("overall_score"),
            "outputs": vault_service.list_outputs(brand_name, video_id),
        }
        result["output_payload"] = _collect_output_payload(brand_name, video_id)
        _update_job(job_id, "completed", "Skill refinada con éxito.", result=result)
    except Exception as error:
        print(f"[Refine] Job {job_id} failed: {error}")
        _update_job(job_id, "failed", "El refinamiento falló.", error=str(error))


def _start_job(
    brand_name: str,
    video_id: str,
    source_type: str,
    source_value: str,
    media_runner: Callable[[Path], Path],
    background_tasks: BackgroundTasks,
    ai_provider: str = settings.AI_DEFAULT_PROVIDER,
    ai_model: Optional[str] = None,
    analysis_modules: Optional[list] = None,
) -> dict:
    _ensure_ai_provider_available(ai_provider)
    job_id = _create_job(brand_name, video_id, source_type, source_value, ai_provider, ai_model, analysis_modules)
    
    # En Cloud (Vercel) usamos BackgroundTasks para evitar bloqueos del worker
    # En Local usamos el executor o BackgroundTasks indistintamente
    background_tasks.add_task(
        _process_job, job_id, brand_name, video_id, source_type, media_runner, ai_provider, ai_model, analysis_modules
    )
    
    return _public_job(job_id)


def _start_analysis_job(
    brand_name: str, 
    video_id: str, 
    ai_provider: str, 
    ai_model: Optional[str], 
    analysis_modules: Optional[list],
    background_tasks: BackgroundTasks
) -> dict:
    _ensure_ai_provider_available(ai_provider)
    job_id = _create_job(brand_name, video_id, "analysis", "vault", ai_provider, ai_model, analysis_modules)
    
    background_tasks.add_task(
        _process_analysis_job, job_id, brand_name, video_id, ai_provider, ai_model, analysis_modules
    )
    
    return _public_job(job_id)


def _start_creative_pack_job(
    brand_name: str,
    video_id: str,
    ai_provider: str,
    ai_model: Optional[str],
    fallback_provider: Optional[str],
    background_tasks: BackgroundTasks
) -> dict:
    if ai_provider != "local":
        _ensure_ai_provider_available(ai_provider)
    job_id = _create_job(brand_name, video_id, "creative_pack", "vault", ai_provider, ai_model, [])
    with jobs_lock:
        jobs[job_id]["analysis_modules"] = ["creative_pack"]
        
    background_tasks.add_task(
        _process_creative_pack_job, job_id, brand_name, video_id, ai_provider, ai_model, fallback_provider
    )
    
    return _public_job(job_id)


def _raise_http_error(error: Exception):
    if isinstance(error, HTTPException):
        raise error
    if isinstance(error, (ValueError, FileNotFoundError)):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=500, detail=str(error)) from error


@app.post("/ai/adapt-script")
def adapt_script_endpoint(req: AdaptScriptRequest):
    try:
        adapted_data = brand_shifting_service.adapt_script(
            original_script=req.original_script,
            target_brand=req.target_brand,
            ai_provider=settings.AI_DEFAULT_PROVIDER,
            ai_model=None
        )
        return {"status": "success", "data": adapted_data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/")
def read_root():
    return RedirectResponse(url="/app")


@app.get("/app", response_class=HTMLResponse)
def read_app():
    html_path = STATIC_DIR / "app.html"
    if not html_path.exists():
        # Fallback para Vercel si los paths se mueven en el build
        alt_path = Path(__file__).parent / "static" / "app.html"
        if alt_path.exists():
            html_path = alt_path
            
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró app.html en {html_path}")
        
    return HTMLResponse(html_path.read_text(encoding="utf-8"))



@app.post("/api/generate-brand-image")
def generate_brand_image(request: GenerateImageRequest):
    try:
        image_result = ai_provider_service.generate_image(
            prompt=request.prompt,
            size=request.size,
            model=request.model,
            provider=request.provider,
        )
        url = image_result.get("url")
        
        # Opcional: descargar y guardar en el vault
        video_path = vault_service.get_video_path(request.brand_name, request.video_id)
        if url and video_path.exists():
            creative_dir = video_path / "Analisis" / "CreativeLab"
            creative_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                if image_result.get("b64_json"):
                    img_data = base64.b64decode(image_result["b64_json"])
                    img_filename = f"image_{uuid4().hex[:8]}.png"
                else:
                    import requests
                    img_data = requests.get(url, timeout=30).content
                    img_filename = f"image_{uuid4().hex[:8]}.jpg"
                with open(creative_dir / img_filename, "wb") as f:
                    f.write(img_data)
                
                # Actualizar payload con archivo local
                image_result["local_path"] = str(creative_dir / img_filename)
                return image_result
            except Exception as e:
                print(f"No se pudo guardar la imagen localmente: {e}")
                
        return image_result
    except Exception as e:
        _raise_http_error(e)


@app.get("/ai/status")
def ai_status():
    return ai_provider_service.status()


@app.get("/ai/models")
def ai_models():
    return ai_provider_service.models()


@app.post("/ai/test")
def ai_test(request: AITestRequest):
    try:
        provider = request.provider or settings.AI_DEFAULT_PROVIDER
        if provider not in {"qwen", "huggingface", "openrouter", "gemini", "groq", "ollama"}:
            raise HTTPException(status_code=400, detail=f"Proveedor IA no soportado para texto: {provider}")
        _ensure_ai_provider_available(provider)
        model = request.model or ai_provider_service.default_model_for(provider)
        response = ai_provider_service.generate_text(
            prompt=request.prompt,
            provider=provider,
            model=model,
            json_mode=False,
        )
        return {
            "ok": True,
            "provider": provider,
            "model": model,
            "response": response,
        }
    except Exception as error:
        _raise_http_error(error)



@app.get("/diagnostic")
def diagnostic():
    """Endpoint de diagnóstico para verificar salud del sistema en la nube."""
    ai_stat = ai_provider_service.status()
    ins_conf = insforge_service.configured()
    vault_root = str(settings.VAULT_ROOT)
    
    writable = False
    try:
        test_file = settings.VAULT_ROOT / ".write_test"
        test_file.write_text("ok")
        test_file.unlink()
        writable = True
    except Exception:
        pass

    qwen_live = False
    qwen_error = None
    if ai_stat["qwen"]["available"]:
        try:
            ai_provider_service.generate_text(
                prompt="Ping",
                provider="qwen",
                model=ai_provider_service.default_model_for("qwen"),
                json_mode=False
            )
            qwen_live = True
        except Exception as e:
            qwen_error = str(e)

    gemini_live = False
    gemini_error = None
    if ai_stat["gemini"]["available"]:
        try:
            ai_provider_service.generate_text(
                prompt="Ping", 
                provider="gemini", 
                model=settings.GEMINI_DEFAULT_MODEL,
                json_mode=False
            )
            gemini_live = True
        except Exception as e:
            gemini_error = str(e)

    openrouter_live = False
    openrouter_error = None
    if ai_stat["openrouter"]["available"]:
        try:
            ai_provider_service.generate_text(
                prompt="Ping", 
                provider="openrouter", 
                model=settings.OPENROUTER_DEFAULT_MODEL,
                json_mode=False
            )
            openrouter_live = True
        except Exception as e:
            openrouter_error = str(e)

    groq_live = False
    groq_error = None
    if ai_stat["groq"]["available"]:
        try:
            ai_provider_service.generate_text(
                prompt="Ping", 
                provider="groq", 
                model=settings.GROQ_DEFAULT_MODEL,
                json_mode=False
            )
            groq_live = True
        except Exception as e:
            groq_error = str(e)

    return {
        "status": "ok",
        "cloud_mode": settings.IS_CLOUD,
        "vault": {
            "root": vault_root,
            "writable": writable
        },
        "insforge": {
            "configured": ins_conf,
            "base_url": settings.INSFORGE_BASE_URL
        },
        "qwen": {
            "available": ai_stat["qwen"]["available"],
            "live": qwen_live,
            "error": qwen_error
        },
        "huggingface": {
            "available": ai_stat["huggingface"]["available"],
            "configured": ai_stat["huggingface"]["configured"]
        },
        "fal": {
            "available": ai_stat["fal"]["available"],
            "configured": ai_stat["fal"]["configured"]
        },
        "gemini": {
            "available": ai_stat["gemini"]["available"],
            "live": gemini_live,
            "error": gemini_error
        },
        "openrouter": {
            "available": ai_stat["openrouter"]["available"],
            "live": openrouter_live,
            "error": openrouter_error
        },
        "groq": {
            "available": ai_stat["groq"]["available"],
            "live": groq_live,
            "error": groq_error
        },
        "timestamp": _now()
    }


@app.get("/ollama/status")
def ollama_status():
    return ollama_control_service.status()


@app.post("/ollama/start")
def ollama_start():
    return ollama_control_service.start()


@app.post("/ollama/stop")
def ollama_stop():
    active_jobs = _active_ollama_jobs()
    if active_jobs:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "No se puede apagar Ollama mientras hay jobs activos usándolo.",
                "active_jobs": [{"job_id": job["job_id"], "status": job["status"], "video_id": job["video_id"]} for job in active_jobs],
            },
        )
    return ollama_control_service.stop()


@app.post("/ollama/restart")
def ollama_restart():
    active_jobs = _active_ollama_jobs()
    if active_jobs:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "No se puede reiniciar Ollama mientras hay jobs activos usándolo.",
                "active_jobs": [{"job_id": job["job_id"], "status": job["status"], "video_id": job["video_id"]} for job in active_jobs],
            },
        )
    return ollama_control_service.restart()


@app.get("/config/status")
def config_status():
    ai_status_data = ai_provider_service.status()
    project_root = Path(__file__).resolve().parent.parent
    env_paths = [project_root / ".env", Path.cwd() / ".env"]
    existing_env = next((path for path in env_paths if path.exists()), None)
    qwen_key = settings.DASHSCOPE_API_KEY or settings.DASHSCOPE_API_KEYS or settings.QWEN_API_KEY or settings.QWEN_API_KEYS
    hf_key = settings.HF_TOKEN or settings.HF_TOKENS
    fal_key = settings.FAL_KEY or settings.FAL_KEYS
    gemini_key = settings.GEMINI_API_KEY or settings.GEMINI_API_KEYS
    openrouter_key = settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEYS
    openai_key = settings.OPENAI_API_KEY or settings.OPENAI_API_KEYS

    env_flags = {
        "qwen": False,
        "huggingface": False,
        "fal": False,
        "gemini": False,
        "openrouter": False,
        "openai": False,
    }
    
    if existing_env:
        try:
            content = existing_env.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                name, value = stripped.split("=", 1)
                if not value.strip():
                    continue
                if name in {"DASHSCOPE_API_KEY", "DASHSCOPE_API_KEYS", "QWEN_API_KEY", "QWEN_API_KEYS"}:
                    env_flags["qwen"] = True
                if name in {"HF_TOKEN", "HF_TOKENS", "HUGGINGFACE_API_KEY", "HUGGINGFACE_API_KEYS"}:
                    env_flags["huggingface"] = True
                if name in {"FAL_KEY", "FAL_KEYS", "FAL_API_KEY", "FAL_API_KEYS"}:
                    env_flags["fal"] = True
                if name in {"GEMINI_API_KEY", "GEMINI_API_KEYS"}:
                    env_flags["gemini"] = True
                if name in {"OPENROUTER_API_KEY", "OPENROUTER_API_KEYS"}:
                    env_flags["openrouter"] = True
                if name in {"OPENAI_API_KEY", "OPENAI_API_KEYS"}:
                    env_flags["openai"] = True
        except OSError:
            pass

    def source_for(active: bool, env_flag: bool) -> Optional[str]:
        if active:
            return "process_env_or_loaded_env"
        if env_flag:
            return "env_file_pending_restart"
        return None

    restart_required = (
        (env_flags["qwen"] and not bool(qwen_key))
        or (env_flags["huggingface"] and not bool(hf_key))
        or (env_flags["fal"] and not bool(fal_key))
        or (env_flags["gemini"] and not bool(gemini_key))
        or (env_flags["openrouter"] and not bool(openrouter_key))
        or (env_flags["openai"] and not bool(openai_key))
    )

    return {
        "env_file_present": existing_env is not None,
        "env_file_path": str(existing_env) if existing_env else str(project_root / ".env"),
        "env_example_path": str(project_root / ".env.example"),
        "qwen_api_key_configured": bool(qwen_key),
        "qwen_api_key_masked": "********" if qwen_key else None,
        "qwen_api_key_source": source_for(bool(qwen_key), env_flags["qwen"]),
        "qwen_env_file_has_key": env_flags["qwen"],
        "qwen_base_url": settings.QWEN_BASE_URL,
        "qwen_default_model": ai_status_data["qwen"]["default_model"],
        "huggingface_api_key_configured": bool(hf_key),
        "huggingface_env_file_has_key": env_flags["huggingface"],
        "fal_api_key_configured": bool(fal_key),
        "fal_env_file_has_key": env_flags["fal"],
        "gemini_api_key_configured": bool(gemini_key),
        "gemini_api_key_masked": "********" if gemini_key else None,
        "gemini_api_key_source": source_for(bool(gemini_key), env_flags["gemini"]),
        "gemini_env_file_has_key": env_flags["gemini"],
        "openrouter_api_key_configured": bool(openrouter_key),
        "openrouter_env_file_has_key": env_flags["openrouter"],
        "openai_api_key_configured": bool(openai_key),
        "openai_env_file_has_key": env_flags["openai"],
        "default_provider": settings.AI_DEFAULT_PROVIDER,
        "fallback_provider": settings.AI_FALLBACK_PROVIDER,
        "openrouter_default_model": ai_status_data["openrouter"]["default_model"],
        "image_default_provider": settings.IMAGE_DEFAULT_PROVIDER,
        "image_default_model": ai_provider_service.default_model_for(settings.IMAGE_DEFAULT_PROVIDER),
        "model_registry": ai_status_data.get("model_registry", {}),
        "restart_required": restart_required,
        "gemini_sdk_installed": ai_status_data["gemini"]["sdk_installed"],
        "gemini_legacy_sdk_installed": ai_status_data["gemini"]["legacy_sdk_installed"],
        "is_cloud": settings.IS_CLOUD,
        "is_vercel": settings.IS_VERCEL,
        "insforge_configured": insforge_service.configured(),
        "cloud_capabilities": {
            "url_source": True,
            "upload_source": True,
            "local_path_source": not settings.IS_CLOUD,
            "ollama": not settings.IS_CLOUD,
            "qwen": bool(qwen_key),
            "huggingface": bool(hf_key),
            "fal": bool(fal_key),
            "gemini": bool(gemini_key),
            "openrouter": bool(openrouter_key),
            "openai": bool(openai_key),
            "persistent_jobs": insforge_service.configured(),
            "vault_root": str(vault_service.root),
        },
        "setup_note": "Qwen directo es el motor principal. Configura DASHSCOPE_API_KEY o QWEN_API_KEY; FAL_KEY/HF_TOKEN activan media; OPENROUTER_API_KEY queda como respaldo.",
    }


@app.post("/vault/create-video")
def create_vault_entry(request: VaultCreateRequest):
    try:
        path = vault_service.create_video_entry(request.brand_name, request.video_id)
        return {"message": "Directorio creado", "path": str(path)}
    except Exception as error:
        _raise_http_error(error)


@app.post("/media/extract")
def extract_media(request: MediaExtractRequest):
    try:
        _video_path, source_type, audio_file = _run_media_extract(request)
        return {
            "message": "Audio extraído correctamente",
            "audio_path": str(audio_file),
            "source_type": source_type,
        }
    except Exception as error:
        _raise_http_error(error)


@app.post("/transcribe")
def transcribe_audio(request: TranscribeRequest):
    try:
        video_path = vault_service.create_video_entry(request.brand_name, request.video_id)
        result, script_path, metadata_path = _run_transcription(video_path, request.audio_filename)

        return {
            "message": "Transcripción completada",
            "language": result["language_detected"],
            "language_probability": result["language_probability"],
            "script_path": str(script_path),
            "metadata_path": str(metadata_path),
            "script_preview": _preview(result["full_text"], 200),
        }
    except Exception as error:
        _raise_http_error(error)


@app.post("/pipeline/process")
def process_pipeline(request: PipelineProcessRequest):
    try:
        video_path, source_type, audio_file = _run_media_extract(request)
        result, script_path, metadata_path = _run_transcription(video_path)
        analysis_status = analysis_service.analyze_script(video_path, request.brand_name, request.video_id, result["full_text"])
        return _build_result(request.brand_name, request.video_id, source_type, video_path, audio_file, result, script_path, metadata_path, analysis_status)
    except Exception as error:
        _raise_http_error(error)


@app.post("/jobs/process-url")
def create_url_job(request: JobUrlRequest, background_tasks: BackgroundTasks):
    try:
        media_service.validate_url_source(request.url)

        def runner(video_path: Path) -> Path:
            audio_file = media_service.process_url(request.url, video_path)
            vault_service.save_json(video_path, "source_metadata.json", {
                "source_type": "url",
                "source_value": request.url,
                "processed_at": _now(),
            })
            return audio_file

        return _start_job(request.brand_name, request.video_id, "url", request.url, runner, background_tasks, request.ai_provider, request.ai_model, request.analysis_modules)
    except Exception as error:
        _raise_http_error(error)


@app.post("/jobs/process")
def create_generic_job(request: JobProcessRequest, background_tasks: BackgroundTasks):
    if request.url:
        return create_url_job(
            JobUrlRequest(
                brand_name=request.brand_name,
                video_id=request.video_id,
                url=request.url,
                ai_provider=request.ai_provider,
                ai_model=request.ai_model,
                analysis_modules=request.analysis_modules,
            ),
            background_tasks=background_tasks
        )
    return create_local_path_job(
        JobLocalPathRequest(
            brand_name=request.brand_name,
            video_id=request.video_id,
            local_file_path=request.local_file_path,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            analysis_modules=request.analysis_modules,
        ),
        background_tasks=background_tasks
    )


@app.post("/jobs/process-local-path")
def create_local_path_job(request: JobLocalPathRequest, background_tasks: BackgroundTasks):
    try:
        if settings.IS_CLOUD:
            raise HTTPException(
                status_code=400,
                detail="La fuente por ruta local solo está disponible en modo local. En cloud usa URL o subida de archivo.",
            )
        local_path = Path(request.local_file_path).expanduser()
        if not local_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo local: {local_path}")
        if not local_path.is_file():
            raise ValueError(f"La ruta local no apunta a un archivo: {local_path}")

        def runner(video_path: Path) -> Path:
            audio_file = media_service.process_local_file(local_path, video_path)
            vault_service.save_json(video_path, "source_metadata.json", {
                "source_type": "local_path",
                "source_value": str(local_path),
                "processed_at": _now(),
            })
            return audio_file

        return _start_job(request.brand_name, request.video_id, "local_path", str(local_path), runner, background_tasks, request.ai_provider, request.ai_model, request.analysis_modules)
    except Exception as error:
        _raise_http_error(error)


@app.post("/jobs/process-upload")
def create_upload_job(
    background_tasks: BackgroundTasks,
    brand_name: str = Form(...),
    video_id: str = Form(...),
    ai_provider: str = Form(settings.AI_DEFAULT_PROVIDER),
    ai_model: Optional[str] = Form(None),
    analysis_modules: Optional[str] = Form(None),
    file: UploadFile = File(...),
):
    try:
        uploaded_path = vault_service.save_uploaded_file(brand_name, video_id, file.filename, file.file)

        def runner(video_path: Path) -> Path:
            audio_file = media_service.process_local_file(uploaded_path, video_path)
            vault_service.save_json(video_path, "source_metadata.json", {
                "source_type": "upload",
                "source_value": str(uploaded_path),
                "original_filename": file.filename,
                "processed_at": _now(),
            })
            return audio_file

        modules = [item.strip() for item in analysis_modules.split(",") if item.strip()] if analysis_modules else None
        return _start_job(brand_name, video_id, "upload", str(uploaded_path), runner, background_tasks, ai_provider, ai_model, modules)
    except Exception as error:
        _raise_http_error(error)
    finally:
        file.file.close()


@app.post("/jobs/analyze/{brand_name}/{video_id}")
def analyze_existing_video(brand_name: str, video_id: str, request: AnalyzeJobRequest, background_tasks: BackgroundTasks):
    try:
        return _start_analysis_job(brand_name, video_id, request.ai_provider, request.ai_model, request.analysis_modules, background_tasks)
    except Exception as error:
        _raise_http_error(error)


@app.post("/jobs/refine/{brand_name}/{video_id}")
def refine_existing_analysis(brand_name: str, video_id: str, request: RefineJobRequest, background_tasks: BackgroundTasks):
    try:
        _ensure_ai_provider_available(request.ai_provider)
        job_id = _create_job(brand_name, video_id, "refine", "vault", request.ai_provider, request.ai_model, [])
        background_tasks.add_task(
            _process_refine_job, job_id, brand_name, video_id, request.ai_provider, request.ai_model
        )
        return _public_job(job_id)
    except Exception as error:
        _raise_http_error(error)


@app.get("/training/evolution/{brand_name}")
def get_brand_evolution(brand_name: str):
    try:
        from services.training_service import training_service
        brand_path = vault_service.create_brand_structure(brand_name)
        return vault_service.read_json(brand_path / "Analisis" / "evolucion_skills.json") or {"history": [], "current_level": "novice"}
    except Exception as error:
        _raise_http_error(error)

@app.post("/training/consolidate/{brand_name}")
def consolidate_brand_wisdom(brand_name: str, ai_provider: str = settings.AI_DEFAULT_PROVIDER):
    """Sintetiza lo aprendido de las auditorías en reglas de marca definitivas."""
    try:
        try:
            from services.training_service import training_service
        except ModuleNotFoundError:
            from backend.services.training_service import training_service
        wisdom = training_service.consolidate_brand_intelligence(brand_name, ai_provider=ai_provider)
        if not wisdom:
            raise HTTPException(status_code=404, detail="No hay suficiente historia para consolidar sabiduría.")
        return wisdom
    except Exception as error:
        _raise_http_error(error)

@app.get("/training/wisdom/{brand_name}")
def get_brand_wisdom(brand_name: str):
    """Obtiene la sabiduría de marca consolidada."""
    try:
        brand_path = vault_service.create_brand_structure(brand_name)
        wisdom = vault_service.read_json(brand_path / "Analisis" / "sabiduria_marca.json")
        return wisdom or {}
    except Exception as error:
        _raise_http_error(error)


@app.get("/jobs/{job_id}")
def read_job(job_id: str):
    job = _public_job_from_cache_or_store(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado.")
    return job


@app.get("/vault/brands")
def list_brands():
    return {"brands": vault_service.list_brands()}


@app.get("/vault/brands/{brand_name}/videos")
def list_brand_videos(brand_name: str):
    return {"brand_name": brand_name, "videos": vault_service.list_videos(brand_name)}


@app.get("/vault/brands/{brand_name}/videos/{video_id}")
def describe_brand_video(brand_name: str, video_id: str):
    video_path = vault_service.get_video_path(brand_name, video_id)
    if not video_path.exists() and not insforge_service.get_video_script(brand_name, video_id):
        raise HTTPException(status_code=404, detail="Video no encontrado en el Vault.")
    return vault_service.describe_video(brand_name, video_id)


@app.get("/vault/brands/{brand_name}/profile")
def read_brand_profile(brand_name: str):
    try:
        return vault_service.get_brand_profile(brand_name)
    except Exception as error:
        _raise_http_error(error)


@app.put("/vault/brands/{brand_name}/profile")
def update_brand_profile(brand_name: str, request: BrandProfileRequest):
    try:
        data = request.model_dump(exclude_none=True)
        return vault_service.save_brand_profile(brand_name, data)
    except Exception as error:
        _raise_http_error(error)


@app.get("/vault/brands/{brand_name}/videos/{video_id}/outputs")
def list_video_outputs(brand_name: str, video_id: str):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        if not video_path.exists():
            payload = _stored_output_payload(brand_name, video_id)
            if not payload:
                raise FileNotFoundError("Video no encontrado en el Vault.")
            outputs = []
            for filename in (payload.get("analysis") or {}).keys():
                outputs.append({
                    "key": filename.rsplit(".", 1)[0],
                    "label": filename,
                    "filename": filename,
                    "path": None,
                })
            return {"brand_name": brand_name, "video_id": video_id, "outputs": outputs}
        return {"brand_name": brand_name, "video_id": video_id, "outputs": vault_service.list_outputs(brand_name, video_id)}
    except Exception as error:
        _raise_http_error(error)


@app.get("/creative-pack/{brand_name}/{video_id}")
def read_creative_pack(brand_name: str, video_id: str):
    try:
        pack = creative_pack_service.read_pack(brand_name, video_id)
        paths = creative_pack_service.pack_paths(brand_name, video_id)
        if not pack:
            payload = _stored_output_payload(brand_name, video_id)
            pack = (payload.get("creative_pack") or {}).get("json") or {}
        return {
            "brand_name": brand_name,
            "video_id": video_id,
            "pack": pack,
            "files": {
                "json": str(paths["json"]) if paths["json"].exists() else None,
                "markdown": str(paths["markdown"]) if paths["markdown"].exists() else None,
            },
        }
    except Exception as error:
        _raise_http_error(error)


@app.post("/creative-pack/{brand_name}/{video_id}")
def generate_creative_pack(brand_name: str, video_id: str, request: CreativePackRequest):
    try:
        pack = creative_pack_service.generate_pack(
            brand_name=brand_name,
            video_id=video_id,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            fallback_provider=request.fallback_provider,
        )
        paths = creative_pack_service.pack_paths(brand_name, video_id)
        return {
            "brand_name": brand_name,
            "video_id": video_id,
            "pack": pack,
            "files": {
                "json": str(paths["json"]) if paths["json"].exists() else None,
                "markdown": str(paths["markdown"]) if paths["markdown"].exists() else None,
            },
        }
    except Exception as error:
        _raise_http_error(error)


@app.post("/creative-pack/{brand_name}/{video_id}/job")
def generate_creative_pack_job(brand_name: str, video_id: str, request: CreativePackRequest, background_tasks: BackgroundTasks):
    try:
        return _start_creative_pack_job(
            brand_name=brand_name,
            video_id=video_id,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            fallback_provider=request.fallback_provider,
            background_tasks=background_tasks
        )
    except Exception as error:
        _raise_http_error(error)


@app.get("/creative-pack/{brand_name}/{video_id}/{filename}")
def read_creative_pack_file(brand_name: str, video_id: str, filename: str):
    allowed = {
        "creative_pack.json": "application/json",
        "creative_pack.md": "text/markdown; charset=utf-8",
    }
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Archivo creativo no permitido.")
    try:
        paths = creative_pack_service.pack_paths(brand_name, video_id)
        file_path = paths["json"] if filename.endswith(".json") else paths["markdown"]
        if not file_path.exists():
            payload = _stored_output_payload(brand_name, video_id)
            stored_value = (payload.get("creative_pack") or {}).get("json" if filename.endswith(".json") else "markdown")
            if stored_value is not None:
                if filename.endswith(".json"):
                    return JSONResponse(stored_value)
                return PlainTextResponse(str(stored_value), media_type=allowed[filename])
            raise FileNotFoundError(f"No se encontró {filename}.")
        return FileResponse(file_path, media_type=allowed[filename], filename=filename)
    except Exception as error:
        _raise_http_error(error)


@app.post("/microtasks/run/{brand_name}/{video_id}")
def run_microtasks(brand_name: str, video_id: str, request: MicrotaskRunRequest = MicrotaskRunRequest()):
    try:
        return microtask_service.run(brand_name, video_id, groups=request.groups)
    except Exception as error:
        _raise_http_error(error)


@app.get("/microtasks/report/{brand_name}/{video_id}")
def read_microtask_report(brand_name: str, video_id: str):
    try:
        return microtask_service.read_report(brand_name, video_id)
    except Exception as error:
        _raise_http_error(error)


@app.get("/vault/script/{brand_name}/{video_id}")
def read_script(brand_name: str, video_id: str):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        script_path = video_path / "guion_original.txt"
        if not script_path.exists():
            payload = _stored_output_payload(brand_name, video_id)
            if payload.get("script"):
                return PlainTextResponse(payload["script"], media_type="text/plain; charset=utf-8")
            raise FileNotFoundError(f"No se encontró el guion en {script_path}")
        return FileResponse(script_path, media_type="text/plain; charset=utf-8", filename="guion_original.txt")
    except Exception as error:
        _raise_http_error(error)


@app.get("/vault/metadata/{brand_name}/{video_id}")
def read_metadata(brand_name: str, video_id: str):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        metadata_path = video_path / "metadatos_transcripcion.json"
        if not metadata_path.exists():
            payload = _stored_output_payload(brand_name, video_id)
            if payload.get("metadata"):
                return JSONResponse(payload["metadata"])
            raise FileNotFoundError(f"No se encontraron metadatos en {metadata_path}")
        return FileResponse(metadata_path, media_type="application/json", filename="metadatos_transcripcion.json")
    except Exception as error:
        _raise_http_error(error)


@app.get("/vault/audio/{brand_name}/{video_id}")
def read_audio(brand_name: str, video_id: str):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        audio_path = video_path / "audio_extract.wav"
        if not audio_path.exists():
            raise FileNotFoundError(f"No se encontró el audio en {audio_path}")
        return FileResponse(audio_path, media_type="audio/wav", filename="audio_extract.wav")
    except Exception as error:
        _raise_http_error(error)


@app.get("/vault/analysis/{brand_name}/{video_id}/{filename}")
def read_analysis_file(brand_name: str, video_id: str, filename: str):
    allowed = {
        "resumen_ejecutivo.md": "text/markdown; charset=utf-8",
        "hooks.json": "application/json",
        "momentos_virales.json": "application/json",
        "estructura_narrativa.json": "application/json",
        "ideas_reels.json": "application/json",
        "ads.json": "application/json",
        "brief_creativo.md": "text/markdown; charset=utf-8",
        "captions.json": "application/json",
        "calendario_publicacion.json": "application/json",
        "prompts_visuales.json": "application/json",
        "analisis_visual.json": "application/json",
        "retrospectiva.json": "application/json",
        "prompt_base_marca.json": "application/json",
        "analisis_estado.json": "application/json",
        "auditoria_contexto.json": "application/json",
        "creative_pack.json": "application/json",
        "creative_pack.md": "text/markdown; charset=utf-8",
    }
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Archivo de análisis no permitido.")
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        if filename in {"creative_pack.json", "creative_pack.md"}:
            file_path = video_path / "Analisis" / "CreativeLab" / filename
        else:
            file_path = video_path / "Analisis" / filename
        if not file_path.exists():
            legacy_path = video_path / filename
            file_path = legacy_path if legacy_path.exists() else file_path
        if not file_path.exists():
            payload = _stored_output_payload(brand_name, video_id)
            if filename in {"creative_pack.json", "creative_pack.md"}:
                creative_payload = payload.get("creative_pack") or {}
                stored_value = creative_payload.get("json" if filename.endswith(".json") else "markdown")
            else:
                stored_value = (payload.get("analysis") or {}).get(filename)
            if stored_value is not None:
                if filename.endswith(".json"):
                    return JSONResponse(stored_value)
                return PlainTextResponse(str(stored_value), media_type=allowed[filename])
            raise FileNotFoundError(f"No se encontró {filename} en {video_path}")
        return FileResponse(file_path, media_type=allowed[filename], filename=filename)
    except Exception as error:
        _raise_http_error(error)


@app.get("/vault/frame/{brand_name}/{video_id}/{filename}")
def read_frame(brand_name: str, video_id: str, filename: str):
    try:
        video_path = vault_service.get_video_path(brand_name, video_id)
        frame_path = video_path / "Frames" / filename
        if not frame_path.exists():
            raise FileNotFoundError(f"No se encontró el frame {filename}")
        return FileResponse(frame_path, media_type="image/jpeg", filename=filename)
    except Exception as error:
        _raise_http_error(error)


@app.get("/ai/audit-report")
async def get_audit_report():
    try:
        return context_audit_service.latest_report()
    except Exception as e:
        return {"error": str(e)}


@app.post("/ai/audit-run")
async def run_audit_report():
    try:
        return context_audit_service.audit_all()
    except Exception as e:
        return {"error": str(e)}
