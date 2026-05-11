import os
import sys
import json
import time
from pathlib import Path
from typing import List

# Añadir backend al path para importar servicios
sys.path.append(str(Path(__file__).resolve().parent / "backend"))

try:
    from services.media_service import media_service
    from services.transcription_service import transcription_service
    from services.analysis_service import analysis_service
    from services.insforge_service import insforge_service
    from services.vault_service import vault_service
    from core.config import settings
except ImportError as e:
    print(f"Error importando servicios: {e}")
    sys.exit(1)

def process_single_video(url: str, brand_name: str, ai_provider: str = "openrouter"):
    video_id = f"train_{int(time.time())}"
    print(f"\n--- Procesando: {url} ---")
    
    try:
        # 1. Crear entrada en Vault local
        video_path = vault_service.create_video_entry(brand_name, video_id)
        
        # 2. Registrar en InsForge como 'extracting'
        job_id = f"local_{video_id}"
        insforge_service.create_video_script(brand_name, video_id, url, job_id, status="extracting_audio")
        
        # 3. Extraer audio
        print("Extracting audio...")
        audio_file = media_service.process_url(url, video_path)
        
        # 4. Transcribir
        print("Transcribing...")
        insforge_service.update_video_script_by_job_id(job_id, {"status": "transcribing"})
        transcription, script_path, metadata_path = _run_transcription(video_path)
        
        # 5. Analizar
        print(f"Analyzing with {ai_provider}...")
        insforge_service.update_video_script_by_job_id(job_id, {"status": "analyzing_text"})
        analysis_status = analysis_service.analyze_script(
            video_path,
            brand_name,
            video_id,
            transcription["full_text"],
            ai_provider=ai_provider
        )
        
        # 6. Finalizar y Sincronizar
        print("Finalizing and Syncing to InsForge...")
        result = _build_result(brand_name, video_id, video_path, audio_file, transcription, script_path, metadata_path, analysis_status)
        
        # Actualizar InsForge con el resultado final
        updates = {
            "status": "completed",
            "original_script": transcription["full_text"],
            "creative_prompts": result,
            "analyzed_script": json.dumps({"job_state": {"status": "completed", "result": result}}, ensure_ascii=False)
        }
        insforge_service.update_video_script_by_job_id(job_id, updates)
        print(f"✅ Éxito: {video_id} sincronizado.")
        
    except Exception as e:
        print(f"❌ Error procesando {url}: {e}")
        insforge_service.update_video_script_by_job_id(job_id, {"status": "failed", "analyzed_script": json.dumps({"error": str(e)})})

def _run_transcription(video_path: Path):
    audio_path = video_path / "audio_extract.wav"
    result = transcription_service.transcribe_audio(audio_path)
    script_path = vault_service.save_file(video_path, "guion_original.txt", result["full_text"])
    metadata_path = vault_service.save_json(video_path, "metadatos_transcripcion.json", result)
    return result, script_path, metadata_path

def _build_result(brand_name, video_id, video_path, audio_file, transcription, script_path, metadata_path, analysis_status):
    return {
        "status": "completed",
        "brand_name": brand_name,
        "video_id": video_id,
        "source_type": "url",
        "vault_path": str(video_path),
        "script_preview": transcription["full_text"][:500],
        "analysis_status": analysis_status
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ScriptDNA Local Training Engine")
    parser.add_argument("--urls", nargs="+", help="URLs de YouTube a procesar")
    parser.add_argument("--brand", default="MassTest", help="Nombre de la marca")
    parser.add_argument("--provider", default="openrouter", help="Proveedor IA")
    
    args = parser.parse_args()
    
    if not args.urls:
        print("Por favor proporciona URLs con --urls")
        sys.exit(1)
        
    for url in args.urls:
        process_single_video(url, args.brand, args.provider)
