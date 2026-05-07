import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Setup paths
workspace_path = Path("/Users/mariomorera/Desktop/APP Extración de Guiones")
sys.path.append(str(workspace_path / "backend"))

# Import services
from services.media_service import media_service
from services.transcription_service import transcription_service
from services.analysis_service import analysis_service
from services.vault_service import vault_service
from services.context_audit_service import context_audit_service
from services.visual_service import visual_service

REEL_DIR = Path("/Users/mariomorera/Desktop/REEL")
TEST_BRAND = "MassTest_Reels"

def mass_test():
    print(f"🚀 Iniciando Testeo Masivo de Reels en: {REEL_DIR}")
    
    # 1. Asegurar perfil de marca para el test
    brand_profile = {
        "brand_name": TEST_BRAND,
        "tone": "Directo, experto, Quiet Luxury",
        "audience": "Dueños de agencias y creadores de contenido",
        "offer": "Sistemas de automatización de contenido",
        "visual_style": "Minimalista, high-fidelity, contrastado",
        "forbidden_words": ["barato", "oferton", "increible"],
        "cta": "Reserva una llamada de estrategia"
    }
    vault_service.save_brand_profile(TEST_BRAND, brand_profile)
    
    reels = sorted(list(REEL_DIR.glob("*.mp4")))
    results = []

    for i, reel_path in enumerate(reels):
        video_id = reel_path.stem.replace(" ", "_")
        print(f"\n[{i+1}/{len(reels)}] Procesando: {video_id}...")
        
        try:
            # A. Preparar Directorios
            video_vault_path = vault_service.get_video_path(TEST_BRAND, video_id)
            video_vault_path.mkdir(parents=True, exist_ok=True)
            analysis_dir = video_vault_path / "Analisis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if already processed and GOOD
            audit_path = analysis_dir / "auditoria_contexto.json"
            if audit_path.exists():
                audit = vault_service.read_json(audit_path)
                # Si el score es alto y no hubo error de visión, podemos saltar (o no, según queramos re-testear la nueva lógica)
                visual_status = audit.get("context", {}).get("visual_context_status")
                if audit.get("overall_score", 0) >= 8.0 and visual_status not in ("error", "missing"):
                    print(f"   ⏩ SALTANDO: {video_id} ya tiene score {audit['overall_score']}")
                    results.append({
                        "video_id": video_id,
                        "score": audit["overall_score"],
                        "status": audit["status"],
                        "warnings": len(audit["warnings"])
                    })
                    continue
                else:
                    print(f"   🔄 RE-PROCESANDO: Score previo {audit.get('overall_score')} o error visual ({visual_status})")

            # B. Extraer Audio y Transcribir (Solo si no existe)
            audio_path = video_vault_path / "audio_extract.wav"
            if not audio_path.exists():
                print("   - Extrayendo audio...")
                audio_path = media_service.process_local_file(reel_path, video_vault_path)
            
            guion_path = video_vault_path / "guion_original.txt"
            if not guion_path.exists():
                print("   - Transcribiendo...")
                transcription = transcription_service.transcribe_audio(audio_path)
                vault_service.save_file(video_vault_path, "guion_original.txt", transcription["full_text"])
                vault_service.save_json(video_vault_path, "metadatos_transcripcion.json", transcription)
            else:
                transcription = vault_service.read_json(video_vault_path / "metadatos_transcripcion.json")

            # C. Extraer Frames y Analizar Visualmente
            print("   - Extrayendo frames...")
            visual_service.extract_frames(reel_path, TEST_BRAND, video_id)
            print("   - Analizando contexto visual...")
            visual_context = visual_service.analyze_frames(TEST_BRAND, video_id, transcription["full_text"])
            vault_service.save_json(analysis_dir, "analisis_visual.json", visual_context)
            
            # D. Análisis de Negocio (Lateral Thinking)
            print("   - Generando análisis creativo (Pensamiento Lateral + Coherencia Visual)...")
            analysis_status = analysis_service.analyze_script(
                video_path=video_vault_path,
                brand_name=TEST_BRAND,
                video_id=video_id,
                script_text=transcription["full_text"],
                ai_provider="gemini",
                ai_model="gemini-flash-latest"
            )
            
            # E. Auditoría
            print("   - Ejecutando Auditoría...")
            audit = context_audit_service.audit_video(TEST_BRAND, video_id)
            
            results.append({
                "video_id": video_id,
                "score": audit["overall_score"],
                "status": audit["status"],
                "warnings": len(audit["warnings"])
            })
            
            print(f"   ✅ COMPLETADO. Score: {audit['overall_score']}/10")
            
        except Exception as e:
            print(f"   ❌ ERROR en {video_id}: {str(e)}")
            results.append({"video_id": video_id, "error": str(e)})

    # F. Reporte Final
    print("\n" + "="*50)
    print("📊 REPORTE FINAL DE TESTEO MASIVO (EVOLUCIONADO)")
    print("="*50)
    print(f"{'Video ID':<15} | {'Score':<6} | {'Status':<12} | {'Warns':<5}")
    print("-" * 50)
    for r in results:
        if "error" in r:
            print(f"{r['video_id']:<15} | ERROR: {r['error'][:25]}...")
        else:
            print(f"{r['video_id']:<15} | {r['score']:<6} | {r['status']:<12} | {r['warnings']:<5}")
    print("="*50)
    
    # G. Consolidar Inteligencia de Marca (Cierre de Entrenamiento)
    print("\n🧠 Consolidando Inteligencia de Marca (Pensamiento Lateral)...")
    try:
        from services.training_service import training_service
        intelligence = training_service.consolidate_brand_intelligence(TEST_BRAND, ai_provider="gemini")
        if intelligence:
            print(f"✅ Sabiduría de marca consolidada para: {TEST_BRAND}")
            print(f"   Próximo paso: {intelligence.get('proximo_paso_entrenamiento', 'Continuar analizando.')}")
    except Exception as e:
        print(f"⚠️ No se pudo consolidar inteligencia: {e}")

if __name__ == "__main__":
    mass_test()
