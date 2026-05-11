# ScriptDNA - Protocolo de Testeo Masivo (v2)

## Arquitectura: Local Engine + Cloud Dashboard

```
┌─────────────────────┐     Sync resultados     ┌──────────────────┐
│   TU MAC (Motor)    │ ────────────────────── → │    InsForge DB   │
│                     │                          │ (Cloud Persistente)│
│  local_batch_engine │                          └────────┬─────────┘
│  - FFmpeg           │                                   │
│  - Whisper local    │                                   │ Lee datos
│  - Gemini API       │                                   ▼
│  - Análisis         │                          ┌──────────────────┐
│  - Auditoría        │                          │   Vercel (UI)    │
│  - Creative Pack    │                          │  Dashboard solo  │
└─────────────────────┘                          │  lectura/consulta│
                                                 └──────────────────┘
```

**¿Por qué?** Vercel Serverless mata los BackgroundTasks después de enviar la respuesta HTTP.
El procesamiento pesado debe ejecutarse localmente. Vercel sirve como dashboard de consulta.

---

## Modo 1: Motor Local (RECOMENDADO)

### Requisitos
- venv con `requirements-local.txt` (faster-whisper, etc.)
- `.env` configurado con `GEMINI_API_KEY` y variables InsForge

### Ejecución
```bash
cd /Users/mariomorera/Desktop/APP\ Extración\ de\ Guiones
./backend/venv/bin/python3 backend/tools/local_batch_engine.py \
    --dir ~/Desktop/REEL \
    --brand MassTest_Final \
    --limit 5
```

### Opciones
| Flag | Descripción |
|------|-------------|
| `--dir` | Carpeta con videos (.mp4, .mov, .webm) |
| `--brand` | Nombre de marca para agrupar resultados |
| `--provider` | `gemini` (default) o `ollama` |
| `--limit` | Procesar solo N videos (0 = todos) |
| `--skip-creative` | Saltar generación del creative pack |

### Verificación post-batch
```bash
# Ver resultados en la UI cloud
open https://scriptdna-preview.vercel.app/app

# Verificar via API
curl https://scriptdna-preview.vercel.app/vault/brands/MassTest_Final/videos
```

---

## Modo 2: Test Remoto vía Vercel (SECUNDARIO)

Para cuando necesites validar que el pipeline cloud funciona end-to-end.

> **Advertencia**: Vercel tiene timeout de 60s y BackgroundTasks poco fiables.
> Solo usar para validación puntual, no para batch masivo.

```bash
python3 backend/tools/remote_mass_test.py \
    --dir ~/Desktop/REEL \
    --brand MassTest_Remote \
    --limit 2
```

---

## KPIs de Éxito

| Métrica | Objetivo | Acción si falla |
|---------|----------|-----------------|
| **Success Rate** | > 90% | Revisar errores de Gemini en el reporte JSON |
| **Audit Score** | > 7.5 | Refinar prompts de `analysis_service` |
| **Persistencia** | 100% | Verificar conexión InsForge (`/diagnostic`) |
| **Tiempo por video** | < 120s | Verificar modelo Whisper y velocidad de red |

---

## Registro de Incidentes

El batch engine genera automáticamente un reporte JSON en la carpeta de videos:
```
~/Desktop/REEL/batch_report_1746664789.json
```

Para debug manual de un video fallido:
```bash
# Verificar diagnóstico del sistema
./backend/venv/bin/python3 backend/tools/live_preflight.py --json
```
