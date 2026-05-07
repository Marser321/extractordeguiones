import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from services.context_audit_service import context_audit_service
    from services.vault_service import vault_service
except ModuleNotFoundError:
    from backend.services.context_audit_service import context_audit_service
    from backend.services.vault_service import vault_service

brand = "AD Media Solution"
video = "Test 2"

print(f"--- Debug Hallucination for {brand} / {video} ---")
analysis_dir = vault_service.create_analysis_dir(brand, video)
analysis = vault_service.read_json(analysis_dir / "full_analysis.json")
script = vault_service.read_file(vault_service.get_video_path(brand, video) / "guion_original.txt")

if not analysis:
    print("No analysis found")
    sys.exit(1)

# Usando el metodo privado para debuggear (re-implementado aqui para evitar errores de acceso)
import re
import json

def _keywords(text, limit=200):
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]{4,}", (text or "").lower())
    seen = []
    for word in words:
        if word in context_audit_service.STOPWORDS or word in seen:
            continue
        seen.append(word)
        if len(seen) >= limit:
            break
    return seen

def _flatten_text(value):
    if isinstance(value, dict):
        return " ".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_text(item) for item in value)
    return str(value or "")

analysis_text = _flatten_text(analysis)
brand_profile = vault_service.get_brand_profile(brand)
visual_context = vault_service.read_json(analysis_dir / "analisis_visual.json") or {}

all_context = script + json.dumps(brand_profile) + json.dumps(visual_context)
context_keywords = set(_keywords(all_context, limit=200))
proper_nouns = set(re.findall(r"\b[A-Z][a-z]{3,}\b", analysis_text))

print(f"Context Keywords (sample): {list(context_keywords)[:10]}")
print(f"Proper Nouns found in analysis: {len(proper_nouns)}")

hallucinations = []
for noun in proper_nouns:
    if noun in context_audit_service.COMMON_SPANISH_TITLES:
        continue
    if noun.lower() in context_keywords or noun in all_context:
        continue
    hallucinations.append(noun)

print(f"Hallucinations flagged: {len(hallucinations)}")
for h in hallucinations[:50]:
    print(f"  - {h}")
