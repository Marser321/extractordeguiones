import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from services.training_service import training_service
except ModuleNotFoundError:
    from backend.services.training_service import training_service

brands = ["AD Media Solution", "MassTest_Reels"]

for brand in brands:
    print(f"🚀 Consolidando sabiduría para {brand}...")
    wisdom = training_service.consolidate_brand_intelligence(brand, ai_provider="gemini")
    if wisdom:
        print(f"✅ {brand} consolidada. Nivel: {wisdom.get('personalidad_detectada')}")
    else:
        print(f"❌ {brand} no tiene historial suficiente.")
