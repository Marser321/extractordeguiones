import ast, sys

files = [
    'backend/services/insforge_service.py',
    'backend/services/media_service.py',
    'backend/services/ai_provider_service.py',
    'backend/services/transcription_service.py',
    'backend/services/api_key_service.py',
    'backend/services/vault_service.py',
    'backend/services/analysis_service.py',
    'backend/core/config.py',
    'backend/main.py',
    'api/index.py',
    'massive_trainer.py'
]

print("=" * 60)
print("AUDIT: Syntax Validation")
print("=" * 60)
all_ok = True
for f in files:
    try:
        with open(f, 'r') as fh:
            ast.parse(fh.read())
        print(f"  PASS: {f}")
    except FileNotFoundError:
        print(f"  SKIP: {f} (not found)")
    except SyntaxError as e:
        print(f"  FAIL: {f} -> Line {e.lineno}: {e.msg}")
        all_ok = False

print()
if all_ok:
    print("ALL SYNTAX CHECKS PASSED")
else:
    print("SYNTAX ERRORS DETECTED - FIX BEFORE DEPLOY")
    sys.exit(1)
