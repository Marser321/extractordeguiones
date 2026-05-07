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

brand = "MassTest_Reels"
video = "REEL_1"

print(f"--- Debug Hallucination for {brand} / {video} ---")
analysis_dir = vault_service.create_analysis_dir(brand, video)
analysis = vault_service.read_json(analysis_dir / "full_analysis.json")
script = vault_service.read_file(vault_service.get_video_path(brand, video) / "guion_original.txt")

if not analysis:
    print("No analysis found")
    sys.exit(1)

proper_nouns = context_audit_service._extract_proper_nouns(str(analysis))
context_keywords = context_audit_service._extract_keywords(script)
all_context = script.lower()

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
