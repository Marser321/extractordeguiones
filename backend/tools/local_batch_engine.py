#!/usr/bin/env python3
"""
ScriptDNA - Local Batch Engine
==============================
Procesa videos localmente usando los servicios Python directamente.
Sincroniza resultados a InsForge para visualizarlos en el dashboard cloud.

Este es el motor real de batch — evita las limitaciones de Vercel
(timeouts, BackgroundTasks que mueren) ejecutando todo localmente.

Uso:
  cd /Users/mariomorera/Desktop/APP\ Extración\ de\ Guiones
  ./backend/venv/bin/python3 backend/tools/local_batch_engine.py \\
      --dir ~/Desktop/REEL \\
      --brand MassTest_Final \\
      --limit 5

Requisitos:
  - Ejecutar desde la raíz del proyecto
  - venv con requirements-local.txt instalado (faster-whisper, etc.)
  - .env configurado con GEMINI_API_KEY y INSFORGE_*
"""
import os
import sys
import json
import time
import argparse
import traceback
from pathlib import Path

# ── Setup del path del proyecto ────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Forzar que cargue el .env del proyecto
os.environ.setdefault("PYTHONPATH", str(BACKEND_DIR))

# ── Imports de servicios (carga lazy para aislamiento) ─────
def _load_services():
    """Carga servicios bajo demanda para aislar contexto."""
    from services.media_service import media_service
    from services.transcription_service import transcription_service
    from services.analysis_service import analysis_service
    from services.vault_service import vault_service
    from services.insforge_service import insforge_service
    from services.context_audit_service import context_audit_service
    from services.creative_pack_service import creative_pack_service

    return {
        "media": media_service,
        "transcription": transcription_service,
        "analysis": analysis_service,
        "vault": vault_service,
        "insforge": insforge_service,
        "audit": context_audit_service,
        "creative": creative_pack_service,
    }


def process_single_video(
    file_path: Path,
    brand_name: str,
    video_id: str,
    services: dict,
    ai_provider: str = "gemini",
    skip_creative: bool = False,
) -> dict:
    """
    Procesa un solo video end-to-end:
      1. Extrae audio
      2. Transcribe
      3. Analiza con IA
      4. Audita calidad
      5. Genera creative pack (opcional)
      6. Sincroniza a InsForge
    """
    vault = services["vault"]
    media = services["media"]
    transcription = services["transcription"]
    analysis = services["analysis"]
    insforge = services["insforge"]
    audit = services["audit"]
    creative = services["creative"]

    result = {
        "video_id": video_id,
        "file": file_path.name,
        "steps": {},
    }

    # 1. Crear entrada en vault
    video_path = vault.create_video_entry(brand_name, video_id)
    result["vault_path"] = str(video_path)

    # 2. Extraer audio
    print(f"      🎵 Extrayendo audio...")
    t0 = time.time()
    audio_file = media.process_local_file(file_path, video_path)
    result["steps"]["audio"] = {"ok": True, "elapsed": round(time.time() - t0, 1)}

    # 3. Transcribir
    print(f"      📝 Transcribiendo...")
    t0 = time.time()
    trans_result = transcription.transcribe_audio(audio_file)
    script_text = trans_result["full_text"]

    # Guardar guion
    script_path = video_path / "guion_original.txt"
    script_path.write_text(script_text, encoding="utf-8")

    # Guardar metadatos
    metadata = {
        "language_detected": trans_result["language_detected"],
        "language_probability": trans_result["language_probability"],
        "segments_count": len(trans_result["segments"]),
        "provider": trans_result.get("provider", "unknown"),
    }
    vault.save_json(video_path, "metadatos_transcripcion.json", metadata)

    result["steps"]["transcription"] = {
        "ok": True,
        "elapsed": round(time.time() - t0, 1),
        "language": trans_result["language_detected"],
        "words": len(script_text.split()),
        "provider": trans_result.get("provider"),
    }
    print(f"         → {len(script_text.split())} palabras ({trans_result.get('provider', '?')})")

    # 4. Analizar con IA
    print(f"      🧠 Analizando con {ai_provider}...")
    t0 = time.time()
    analysis_status = analysis.analyze_script(
        video_path=video_path,
        brand_name=brand_name,
        video_id=video_id,
        script_text=script_text,
        ai_provider=ai_provider,
    )
    result["steps"]["analysis"] = {
        "ok": True,
        "elapsed": round(time.time() - t0, 1),
        "modules": list(analysis_status.keys()) if isinstance(analysis_status, dict) else [],
    }

    # 5. Auditar calidad
    print(f"      🔍 Auditando calidad...")
    t0 = time.time()
    try:
        audit_result = audit.audit_video(brand_name, video_id, save=True)
        audit_score = audit_result.get("overall_score", 0)
        result["steps"]["audit"] = {
            "ok": True,
            "elapsed": round(time.time() - t0, 1),
            "score": audit_score,
        }
        print(f"         → Score: {audit_score}/10")
    except Exception as e:
        result["steps"]["audit"] = {"ok": False, "error": str(e)}
        audit_score = 0

    # 6. Creative Pack (opcional)
    if not skip_creative:
        print(f"      🎨 Generando creative pack...")
        t0 = time.time()
        try:
            creative.generate_pack(
                brand_name=brand_name,
                video_id=video_id,
                ai_provider=ai_provider,
            )
            result["steps"]["creative_pack"] = {
                "ok": True,
                "elapsed": round(time.time() - t0, 1),
            }
        except Exception as e:
            result["steps"]["creative_pack"] = {"ok": False, "error": str(e)}
            print(f"         ⚠️  Creative pack falló (no crítico): {e}")

    # 7. Sincronizar a InsForge
    print(f"      ☁️  Sincronizando a InsForge...")
    try:
        # Recopilar todo el output
        output_payload = _collect_payload(vault, video_path, brand_name, video_id)
        
        # Verificar si ya existe un registro para este video
        existing = insforge.get_video_script(brand_name, video_id)
        
        if existing:
            # Actualizar registro existente
            updates = {
                "status": "completed",
                "analyzed_script": json.dumps(output_payload, ensure_ascii=False) if output_payload else None,
            }
            insforge.update_video_script(existing["id"], updates)
        else:
            # Crear nuevo registro
            record = insforge.create_video_script(
                brand_name=brand_name,
                video_id=video_id,
                source_value=str(file_path),
                job_id=f"local_{video_id}",
                status="completed",
                job_state=output_payload,
            )
        
        result["steps"]["sync"] = {"ok": True}
        print(f"         → Sincronizado ✅")
    except Exception as e:
        result["steps"]["sync"] = {"ok": False, "error": str(e)}
        print(f"         ⚠️  Sync falló: {e}")

    result["audit_score"] = audit_score
    result["status"] = "completed"
    return result


def _collect_payload(vault, video_path, brand_name, video_id):
    """Recopila los outputs generados para enviar a InsForge."""
    payload = {}

    # Script
    script_path = video_path / "guion_original.txt"
    if script_path.exists():
        payload["script"] = script_path.read_text(encoding="utf-8")

    # Metadata
    meta = vault.read_json(video_path / "metadatos_transcripcion.json")
    if meta:
        payload["metadata"] = meta

    # Analysis files
    analysis_dir = video_path / "Analisis"
    if analysis_dir.exists():
        analysis = {}
        for f in analysis_dir.iterdir():
            if f.is_file() and f.suffix == ".json":
                try:
                    analysis[f.name] = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    pass
            elif f.is_file() and f.suffix == ".md":
                analysis[f.name] = f.read_text(encoding="utf-8")
        if analysis:
            payload["analysis"] = analysis

    # Creative pack
    creative_dir = analysis_dir / "CreativeLab" if analysis_dir.exists() else None
    if creative_dir and creative_dir.exists():
        cp = {}
        cp_json = creative_dir / "creative_pack.json"
        cp_md = creative_dir / "creative_pack.md"
        if cp_json.exists():
            try:
                cp["json"] = json.loads(cp_json.read_text(encoding="utf-8"))
            except Exception:
                pass
        if cp_md.exists():
            cp["markdown"] = cp_md.read_text(encoding="utf-8")
        if cp:
            payload["creative_pack"] = cp

    return payload


def run_batch(
    reel_dir: str,
    brand_name: str,
    ai_provider: str = "gemini",
    limit: int = 0,
    skip_creative: bool = False,
):
    print("=" * 60)
    print("🏭 ScriptDNA - Local Batch Engine")
    print("=" * 60)

    # ── Cargar servicios ───────────────────────────────────
    print("\n📦 Cargando servicios...")
    try:
        services = _load_services()
        print("   ✅ Servicios cargados")
    except Exception as e:
        print(f"   ❌ Error cargando servicios: {e}")
        traceback.print_exc()
        sys.exit(1)

    # ── Verificar Gemini ───────────────────────────────────
    from services.ai_provider_service import ai_provider_service
    status = ai_provider_service.status()
    gemini_available = status.get("gemini", {}).get("available", False)
    if not gemini_available and ai_provider == "gemini":
        print("   ❌ Gemini no disponible. Verifica GEMINI_API_KEY en .env")
        sys.exit(1)
    print(f"   ✅ Gemini disponible ({status['gemini']['keys_available']} llaves)")

    # ── Buscar videos ──────────────────────────────────────
    extensions = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
    reels = sorted(
        [f for f in Path(reel_dir).iterdir() if f.suffix.lower() in extensions]
    )
    if limit > 0:
        reels = reels[:limit]

    if not reels:
        print(f"\n❌ No se encontraron videos en {reel_dir}")
        sys.exit(1)

    print(f"\n🎬 {len(reels)} videos para procesar")
    print(f"   Marca: {brand_name}")
    print(f"   Motor: {ai_provider}")
    print(f"   Creative Pack: {'Sí' if not skip_creative else 'No'}")
    print()

    # ── Procesar ───────────────────────────────────────────
    results = []
    for i, reel_path in enumerate(reels):
        video_id = f"batch_{int(time.time())}_{reel_path.stem[:25].replace(' ', '_')}"
        print(f"  [{i + 1}/{len(reels)}] {reel_path.name}")

        t0 = time.time()
        try:
            result = process_single_video(
                file_path=reel_path,
                brand_name=brand_name,
                video_id=video_id,
                services=services,
                ai_provider=ai_provider,
                skip_creative=skip_creative,
            )
            elapsed = time.time() - t0
            result["total_elapsed"] = round(elapsed, 1)
            results.append(result)
            print(f"      ✅ Total: {elapsed:.0f}s | Audit: {result.get('audit_score', '?')}/10\n")

        except Exception as e:
            elapsed = time.time() - t0
            print(f"      ❌ FALLO: {e}\n")
            results.append({
                "video_id": video_id,
                "file": reel_path.name,
                "status": "failed",
                "error": str(e),
                "total_elapsed": round(elapsed, 1),
            })

    # ── Reporte ────────────────────────────────────────────
    print("=" * 60)
    print("📊 REPORTE DE BATCH LOCAL")
    print("=" * 60)

    ok = [r for r in results if r.get("status") == "completed"]
    fail = [r for r in results if r.get("status") != "completed"]
    scores = [r["audit_score"] for r in ok if "audit_score" in r]
    avg_score = sum(scores) / len(scores) if scores else 0
    total_time = sum(r.get("total_elapsed", 0) for r in results)

    print(f"\n  ✅ Exitosos: {len(ok)}/{len(results)}")
    print(f"  ❌ Fallidos: {len(fail)}/{len(results)}")
    print(f"  📈 Score promedio: {avg_score:.1f}/10")
    print(f"  ⏱  Tiempo total: {total_time:.0f}s ({total_time / 60:.1f} min)\n")

    for r in results:
        icon = "✅" if r.get("status") == "completed" else "❌"
        score = r.get("audit_score", "—")
        elapsed = r.get("total_elapsed", 0)
        print(f"  {icon} {r['file']} | {elapsed:.0f}s | Score: {score}")

    print("=" * 60)

    # Guardar reporte
    report_path = Path(reel_dir) / f"batch_report_{int(time.time())}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "brand": brand_name,
            "ai_provider": ai_provider,
            "summary": {
                "total": len(results),
                "ok": len(ok),
                "failed": len(fail),
                "avg_score": round(avg_score, 2),
                "total_seconds": round(total_time, 1),
            },
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Reporte: {report_path}")

    # KPI check
    if avg_score < 7.5 and scores:
        print(f"\n⚠️  Score promedio ({avg_score:.1f}) por debajo del objetivo (7.5)")
    if len(fail) / max(len(results), 1) > 0.1:
        print(f"\n⚠️  Tasa de fallo ({len(fail)}/{len(results)}) supera el 10%")

    return len(fail) == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScriptDNA Local Batch Engine")
    parser.add_argument("--dir", default=os.path.expanduser("~/Desktop/REEL"),
                        help="Directorio con videos")
    parser.add_argument("--brand", default="MassTest_Local",
                        help="Nombre de marca")
    parser.add_argument("--provider", default="gemini",
                        help="Proveedor IA (gemini/ollama)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limitar cantidad de videos (0 = todos)")
    parser.add_argument("--skip-creative", action="store_true",
                        help="Saltar generación de creative pack")

    args = parser.parse_args()

    success = run_batch(
        reel_dir=args.dir,
        brand_name=args.brand,
        ai_provider=args.provider,
        limit=args.limit,
        skip_creative=args.skip_creative,
    )
    sys.exit(0 if success else 1)
