import os
import json
from pathlib import Path

VAULT_MARCAS = Path("/Users/mariomorera/Desktop/APP Extración de Guiones/Vault/Marcas")
BRAND = "MassTest_Reels"

def repair():
    brand_path = VAULT_MARCAS / BRAND
    contenido_dir = brand_path / "Contenido"
    
    if not contenido_dir.exists():
        print("❌ No se encontró el directorio de contenido.")
        return
        
    for reel_dir in contenido_dir.iterdir():
        if not reel_dir.is_dir(): continue
        
        script_path = reel_dir / "guion_original.txt"
        meta_path = reel_dir / "metadatos_transcripcion.json"
        
        if script_path.exists() and not meta_path.exists():
            print(f"🔧 Reparando {reel_dir.name}...")
            with open(script_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Crear metadata mock
            metadata = {
                "language_detected": "es",
                "language_probability": 1.0,
                "full_text": text,
                "segments": [
                    {
                        "start": 0.0,
                        "end": 10.0, # Estimado
                        "text": text
                    }
                ],
                "provider": "cloud_repair"
            }
            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Generado: metadatos_transcripcion.json")

if __name__ == "__main__":
    repair()
