import sys
import os
import time
from pathlib import Path

# Agregar el path del backend para importar los servicios
backend_path = Path("/Users/mariomorera/Desktop/APP Extración de Guiones/backend")
sys.path.append(str(backend_path))

from services.analysis_service import analysis_service
from services.creative_pack_service import creative_pack_service
from services.vault_service import vault_service

BRAND = "MassTest_Reels"
VIDEOS = ["REEL_2", "REEL_3", "REEL_4", "REEL_5", "REEL_6", "REEL_7", "REEL_8", "REEL_9", "REEL_10"]

print(f"🚀 Iniciando escalado masivo para {BRAND}...")
print(f"Total videos a procesar: {len(VIDEOS)}")

for video in VIDEOS:
    print(f"\n--- 📦 Procesando {video} ---")
    try:
        video_path = vault_service.get_video_path(BRAND, video)
        script_file = video_path / "guion_original.txt"
        
        if not script_file.exists():
            print(f"⚠️ Saltando {video}: No se encontró guion_original.txt")
            continue
            
        script_text = vault_service.read_file(script_file)
        
        # 1. Analisis
        print(f"[{video}] Ejecutando Análisis...")
        analysis_service.analyze_script(video_path, BRAND, video, script_text, ai_provider="gemini")
        
        # 2. Creative Pack
        print(f"[{video}] Generando Creative Pack...")
        creative_pack_service.generate_pack(BRAND, video, ai_provider="gemini")
        
        print(f"✅ {video} completado con éxito.")
        
        # Pequeña pausa para no saturar las cuotas inmediatamente
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error en {video}: {str(e)}")

print("\n✨ Escalado masivo completado.")
