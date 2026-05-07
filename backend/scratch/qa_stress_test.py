import sys
import os
from pathlib import Path
import json
import time

# Añadir el path del backend
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.vault_service import vault_service
from services.media_service import media_service
from services.transcription_service import transcription_service
from services.visual_service import visual_service
from services.analysis_service import analysis_service
from services.ai_provider_service import ai_provider_service
from scratch.qa_judge import qa_judge

TEST_SOURCES = [
    {
        "name": "Local Audio Test (Smoke Test Data)",
        "path": "/Users/mariomorera/Desktop/APP Extración de Guiones/Vault/Marcas/Smoke Test/Contenido/local-job-v2/audio_extract.wav",
        "brand": "Luxury_QA_Test",
        "video_id": "local_v2_audit",
        "brand_profile": {
            "name": "Luxury DNA",
            "tone": "Elegante, minimalista, autoridad silenciosa",
            "cta": "Agenda una sesión privada",
            "visual_style": "Quiet Luxury, colores neutros, tipografía serif"
        }
    }
]

def run_qa_test():
    print("🚀 Iniciando Auditoría de Razonamiento ScriptDNA...")
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "audits": []
    }

    for source in TEST_SOURCES:
        print(f"\n--- Auditando: {source['name']} ---")
        audit_entry = {"source": source["name"], "steps": {}}
        
        try:
            brand_name = source["brand"]
            video_id = source["video_id"]
            
            # 1. Preparar Estructura y Perfil
            vault_service.create_brand_structure(brand_name)
            brand_path = vault_service.marcas_dir / brand_name
            vault_service.save_json(brand_path, "perfil.json", source["brand_profile"])
            
            video_path = vault_service.get_video_path(brand_name, video_id)
            if not video_path.exists():
                video_path.mkdir(parents=True)
            
            # 2. Audio y Transcripción
            print(f"[{source['name']}] Procesando audio local...")
            transcription = transcription_service.transcribe_audio(Path(source["path"]))
            vault_service.save_json(video_path, "transcripcion.json", transcription)
            audit_entry["steps"]["transcription"] = "SUCCESS"
            
            # 3. Análisis de Negocio (Reasoning)
            print(f"[{source['name']}] Generando análisis estratégico (Gemini)...")
            # Forzamos Ollama para asegurar ejecución local sin depender de API keys
            analysis_status = analysis_service.analyze_script(
                video_path=video_path,
                brand_name=brand_name,
                video_id=video_id,
                script_text=transcription["full_text"],
                ai_provider="gemini"
            )
            audit_entry["steps"]["business_analysis"] = "SUCCESS"
            
            # Cargar el análisis generado
            analysis_file = video_path / "Analisis" / "full_analysis.json"
            with open(analysis_file, "r", encoding="utf-8") as f:
                analysis_data = json.load(f)
            
            # 4. Auditoría IA (QA Judge)
            print(f"[{source['name']}] Juez IA evaluando calidad y alineación...")
            evaluation = qa_judge.evaluate_analysis(
                script=transcription["full_text"],
                analysis=analysis_data,
                brand_profile=source["brand_profile"]
            )
            audit_entry["evaluation"] = evaluation
            print(f"[{source['name']}] Veredicto: {evaluation.get('veredicto', 'ERROR')}")
            
        except Exception as e:
            import traceback
            print(f"❌ Error en auditoría {source['name']}: {e}")
            traceback.print_exc()
            audit_entry["error"] = str(e)
            audit_entry["status"] = "FAILED"
        else:
            audit_entry["status"] = "PASSED"
            
        report["audits"].append(audit_entry)

    # Guardar reporte final
    report_path = Path(__file__).resolve().parent / "final_qa_audit_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Auditoría completada. Reporte detallado en: {report_path}")

if __name__ == "__main__":
    run_qa_test()
