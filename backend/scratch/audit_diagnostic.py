import json
import sys
from pathlib import Path

# Agregar el path del backend para importar los servicios
backend_path = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_path))

from services.context_audit_service import context_audit_service
from services.vault_service import vault_service

def diagnostic():
    print("=== SCRIPTDNA AUDIT DIAGNOSTIC ===")
    brands = vault_service.list_brands()
    
    all_audits = []
    
    for brand in brands:
        brand_name = brand["brand_name"]
        print(f"\n> Analizando Marca: {brand_name}")
        videos = vault_service.list_videos(brand_name)
        
        for video in videos:
            video_id = video["video_id"]
            print(f"  - Audidanto video: {video_id}...", end="")
            audit = context_audit_service.audit_video(brand_name, video_id, save=True)
            if audit:
                print(f" OK (Score: {audit['overall_score']})")
                all_audits.append(audit)
            else:
                print(" SKIP (Sin análisis)")

    if not all_audits:
        print("\nNo se encontraron análisis para auditar.")
        return

    # Reporte de Hallazgos
    avg_score = sum(a['overall_score'] for a in all_audits) / len(all_audits)
    print(f"\n{'='*40}")
    print(f"PROMEDIO GLOBAL: {avg_score:.2f}/10")
    print(f"{'='*40}")
    
    # Detalle por métrica
    metrics = all_audits[0]['scores'].keys()
    print("\nDESEMPEÑO POR MÉTRICA:")
    for metric in metrics:
        m_avg = sum(a['scores'].get(metric, 0) for a in all_audits) / len(all_audits)
        status = "✅ BIEN" if m_avg >= 7.5 else "⚠️ MEJORABLE" if m_avg >= 6 else "❌ CRÍTICO"
        print(f"  {metric:<22}: {m_avg:>5.2f}/10  [{status}]")

    # Advertencias recurrentes
    print("\nADVERTENCIAS RECURRENTES (Lo que nos falta):")
    warnings = {}
    for a in all_audits:
        for w in a['warnings']:
            warnings[w] = warnings.get(w, 0) + 1
    
    sorted_warnings = sorted(warnings.items(), key=lambda x: x[1], reverse=True)
    for w, count in sorted_warnings[:5]:
        print(f"  [{count} videos] {w}")

    print(f"\n{'='*40}")
    print("Diagnóstico completado. Los reportes individuales están en cada Vault.")

if __name__ == "__main__":
    diagnostic()
