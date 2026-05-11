#!/usr/bin/env python3
"""
ScriptDNA - Remote Mass Tester v2
=================================
Procesa lotes de videos locales contra la API desplegada en Vercel.

Arquitectura:
  1. Sube cada video vía multipart a /jobs/process-upload
  2. Espera (polling en /jobs/{job_id}) a que termine o falle
  3. Genera reporte de resultados

Uso:
  python3 remote_mass_test.py --dir ~/Desktop/REEL --brand MassTest_V2
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Instala requests: pip install requests")
    sys.exit(1)


DEFAULT_API_BASE = os.getenv(
    "SCRIPTDNA_API_BASE", "https://scriptdna-preview.vercel.app"
)
POLL_INTERVAL = 5       # segundos entre polls
POLL_TIMEOUT = 300      # timeout total por job (5 min)
CONCURRENCY_DELAY = 3   # pausa entre jobs para no saturar Gemini


class RemoteMassTester:
    def __init__(self, api_base: str):
        self.api_base = api_base.rstrip("/")
        self.session = requests.Session()

    # ── Preflight ──────────────────────────────────────────────
    def preflight(self) -> dict:
        """Verifica que el backend esté disponible y Gemini funcione."""
        url = f"{self.api_base}/diagnostic"
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data
        except Exception as e:
            return {"error": str(e)}

    # ── Upload + Job ───────────────────────────────────────────
    def submit_job(self, file_path: Path, brand_name: str, video_id: str) -> str:
        """Sube un video y dispara el procesamiento vía multipart."""
        url = f"{self.api_base}/jobs/process-upload"
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "video/mp4")}
            data = {
                "brand_name": brand_name,
                "video_id": video_id,
                "ai_provider": "gemini",
            }
            resp = self.session.post(url, files=files, data=data, timeout=120)

        resp.raise_for_status()
        result = resp.json()
        return result["job_id"]

    # ── Polling ────────────────────────────────────────────────
    def poll_job(self, job_id: str) -> dict:
        """Espera a que el job termine, con backoff exponencial."""
        url = f"{self.api_base}/jobs/{job_id}"
        start = time.time()
        interval = POLL_INTERVAL

        while time.time() - start < POLL_TIMEOUT:
            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"      ⚠️  Error de polling: {e}")
                time.sleep(interval)
                continue

            status = data.get("status", "unknown")
            message = data.get("message", "")
            progress = data.get("progress", 0)

            print(f"      [{progress:3d}%] {status}: {message}     ", end="\r")

            if status == "completed":
                print()
                return data
            if status == "failed":
                print()
                return data

            time.sleep(interval)
            # Backoff suave: máximo 15s
            interval = min(interval * 1.2, 15)

        print()
        return {"status": "timeout", "error": f"Timeout después de {POLL_TIMEOUT}s"}


def run_mass_test(reel_dir: str, brand_name: str, api_base: str, limit: int = 0):
    tester = RemoteMassTester(api_base)

    # ── Preflight ──────────────────────────────────────────
    print("🔍 Preflight check...")
    diag = tester.preflight()
    if "error" in diag:
        print(f"❌ Backend no disponible: {diag['error']}")
        sys.exit(1)

    gemini_ok = diag.get("gemini", {}).get("live_test", False)
    gemini_err = diag.get("gemini", {}).get("error")
    if not gemini_ok:
        print(f"⚠️  Gemini live test falló: {gemini_err}")
        print("   El procesamiento puede fallar. ¿Continuar? (s/N)")
        if input().strip().lower() != "s":
            sys.exit(0)
    else:
        print("✅ Backend OK. Gemini operacional.")

    # ── Recopilar archivos ─────────────────────────────────
    extensions = {".mp4", ".mov", ".webm", ".mkv"}
    reels = sorted(
        [f for f in Path(reel_dir).iterdir() if f.suffix.lower() in extensions]
    )
    if limit > 0:
        reels = reels[:limit]

    if not reels:
        print(f"❌ No se encontraron videos en {reel_dir}")
        sys.exit(1)

    print(f"🎬 {len(reels)} videos para procesar contra {api_base}\n")

    # ── Procesar secuencialmente ───────────────────────────
    results = []
    for i, reel_path in enumerate(reels):
        video_id = f"test_{int(time.time())}_{reel_path.stem[:30].replace(' ', '_')}"
        print(f"[{i + 1}/{len(reels)}] {reel_path.name}")

        t0 = time.time()
        try:
            # 1. Submit
            print(f"   ⬆️  Subiendo ({reel_path.stat().st_size / 1024 / 1024:.1f} MB)...")
            job_id = tester.submit_job(reel_path, brand_name, video_id)
            print(f"   🚀 Job creado: {job_id}")

            # 2. Poll
            print(f"   ⏳ Monitoreando...")
            result = tester.poll_job(job_id)

            elapsed = time.time() - t0
            status = result.get("status", "unknown")
            results.append({
                "video": reel_path.name,
                "job_id": job_id,
                "status": status,
                "message": result.get("message", result.get("error", "")),
                "elapsed_s": round(elapsed, 1),
            })

            if status == "completed":
                print(f"   ✅ Completado en {elapsed:.0f}s")
            else:
                print(f"   ❌ {status}: {result.get('error', result.get('message', ''))}")

        except requests.exceptions.ConnectionError:
            print(f"   ❌ Error de conexión — backend caído o timeout de Vercel")
            results.append({
                "video": reel_path.name,
                "status": "connection_error",
                "message": "Backend no respondió (posible timeout de Vercel)",
                "elapsed_s": round(time.time() - t0, 1),
            })
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            results.append({
                "video": reel_path.name,
                "status": "error",
                "message": str(e),
                "elapsed_s": round(time.time() - t0, 1),
            })

        # Pausa entre jobs para no saturar cuota de Gemini
        if i < len(reels) - 1:
            print(f"   ⏸️  Esperando {CONCURRENCY_DELAY}s antes del siguiente job...\n")
            time.sleep(CONCURRENCY_DELAY)

    # ── Reporte ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("📊 REPORTE DE TESTEO REMOTO MASIVO")
    print("=" * 60)

    ok = sum(1 for r in results if r["status"] == "completed")
    fail = len(results) - ok
    total_time = sum(r.get("elapsed_s", 0) for r in results)

    print(f"\n  Total: {len(results)} | ✅ {ok} | ❌ {fail} | ⏱ {total_time:.0f}s\n")

    for r in results:
        icon = "✅" if r["status"] == "completed" else "❌"
        print(f"  {icon} {r['video']} ({r.get('elapsed_s', 0):.0f}s) — {r['message']}")

    print("=" * 60)

    # Guardar reporte
    report_path = Path(reel_dir) / f"mass_test_report_{int(time.time())}.json"
    with open(report_path, "w") as f:
        json.dump({"brand": brand_name, "api_base": api_base, "results": results}, f, indent=2)
    print(f"\n📄 Reporte guardado en: {report_path}")

    return ok == len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScriptDNA Remote Mass Tester v2")
    parser.add_argument("--dir", default=os.path.expanduser("~/Desktop/REEL"),
                        help="Directorio con videos (.mp4, .mov, .webm)")
    parser.add_argument("--brand", default="MassTest_Remote",
                        help="Nombre de marca para los resultados")
    parser.add_argument("--url", default=DEFAULT_API_BASE,
                        help="URL del backend desplegado")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limitar cantidad de videos (0 = todos)")

    args = parser.parse_args()

    success = run_mass_test(args.dir, args.brand, args.url, args.limit)
    sys.exit(0 if success else 1)
