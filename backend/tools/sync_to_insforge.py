import os
import json
import sys
from pathlib import Path

# Añadir el path del backend para poder importar servicios
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from backend.services.insforge_service import insforge_service
    from backend.services.vault_service import vault_service
except ImportError:
    from services.insforge_service import insforge_service
    from services.vault_service import vault_service

def sync():
    print("🚀 Iniciando sincronización de Vault Local -> InsForge Cloud...")
    
    # 1. Sincronizar Marcas
    brands = vault_service.list_brands()
    print(f"📦 Encontradas {len(brands)} marcas locales.")
    
    for b in brands:
        name = b["brand_name"]
        print(f"  -> Sincronizando marca: {name}...")
        profile = vault_service.get_brand_profile(name)
        success = insforge_service.create_or_update_brand(profile)
        if success:
            print(f"     ✅ Marca '{name}' sincronizada.")
        else:
            print(f"     ❌ Error sincronizando marca '{name}'.")

    # 2. Sincronizar Scripts/Jobs
    for b in brands:
        name = b["brand_name"]
        videos = vault_service.list_videos(name)
        print(f"\n🎥 Sincronizando {len(videos)} videos para '{name}'...")
        for v in videos:
            v_id = v["video_id"]
            # Verificar si tiene análisis
            outputs = vault_service.list_outputs(name, v_id)
            if outputs:
                print(f"  -> Sincronizando script: {v_id}...")
                # El servicio ya tiene lógica para sincronizar al guardar o cargar
                # Pero forzaremos una carga/guardado para asegurar persistencia
                try:
                    # Simular carga para disparar la persistencia en InsForge
                    _ = vault_service.describe_video(name, v_id)
                    print(f"     ✅ Script '{v_id}' sincronizado.")
                except Exception as e:
                    print(f"     ❌ Error sincronizando script '{v_id}': {e}")

    print("\n✨ Sincronización completada.")
    print("Ahora la versión online debería mostrar tus marcas.")

if __name__ == "__main__":
    sync()
