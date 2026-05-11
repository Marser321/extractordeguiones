# AD MediaSolution Studio - app local full funcional

AD MediaSolution Studio usa ScriptDNA como motor interno para procesar videos, extraer audio, transcribir guiones en espanol, guardar resultados en un Vault por marca/pieza y generar activos creativos con Gemini u Ollama local.

## Requisitos

- Python con el entorno virtual ya creado en `backend/venv`.
- FFmpeg instalado y disponible en el PATH.
- Ollama local, si quieres usar IA sin API externa.
- Opcional local: `GEMINI_API_KEY` en `.env` o variable de entorno.

## Arranque

Desde la raiz del proyecto:

```bash
PYTHONPATH=backend backend/venv/bin/uvicorn main:app --reload
```

Abre la app:

```text
http://127.0.0.1:8000/app
```

Documentacion interactiva:

```text
http://127.0.0.1:8000/docs
```

## Flujo principal

En la pestana `Procesar` puedes crear jobs con tres fuentes:

- `URL`: descarga y extrae audio con `yt-dlp`.
- `Subir archivo`: selecciona un video/audio desde el navegador; la app lo copia al Vault.
- `Ruta local`: procesa una ruta absoluta del Mac, por ejemplo `/Users/usuario/video.mp4`.

Tambien puedes elegir proveedor/modelo de IA:

- `Ollama local`: usa modelos locales como `llama3:latest`.
- `Gemini API`: usa `GEMINI_API_KEY` desde `.env`.

La UI consulta el job hasta que termina o falla. Los resultados quedan en:

```text
Vault/Marcas/{marca}/Contenido/{video_id}/
```

Archivos esperados:

- `original_video/{archivo}` cuando se usa subida desde navegador.
- `audio_extract.wav`
- `guion_original.txt`
- `metadatos_transcripcion.json`
- `source_metadata.json`
- `Analisis/analisis_estado.json`
- `Analisis/resumen_ejecutivo.md`
- `Analisis/hooks.json`
- `Analisis/momentos_virales.json`
- `Analisis/estructura_narrativa.json`
- `Analisis/ideas_reels.json`
- `Analisis/ads.json`
- `Analisis/brief_creativo.md`
- `Analisis/captions.json`
- `Analisis/calendario_publicacion.json`
- `Analisis/prompts_visuales.json`
- `Analisis/prompt_base_marca.json`
- `Analisis/analisis_visual.json`
- `Analisis/retrospectiva.json`

## Endpoints de jobs

```http
POST /jobs/process-url
POST /jobs/process-upload
POST /jobs/process-local-path
GET /jobs/{job_id}
POST /jobs/analyze/{brand_name}/{video_id}
```

Ejemplo con ruta local:

```json
{
  "brand_name": "Mi Marca",
  "video_id": "video-001",
  "local_file_path": "/Users/usuario/video.mp4"
}
```

## Vault

La pestana `Vault` lista marcas, videos y archivos generados. La pestana `Marca` edita el perfil de marca que la IA usa para adaptar tono, CTA, audiencia y estilo visual. La pestana `Outputs` permite abrir/copiar los activos generados.

Endpoints:

```http
GET /vault/brands
GET /vault/brands/{brand_name}/videos
GET /vault/brands/{brand_name}/videos/{video_id}
GET /vault/brands/{brand_name}/profile
PUT /vault/brands/{brand_name}/profile
GET /vault/brands/{brand_name}/videos/{video_id}/outputs
GET /vault/script/{brand_name}/{video_id}
GET /vault/metadata/{brand_name}/{video_id}
GET /vault/audio/{brand_name}/{video_id}
GET /vault/analysis/{brand_name}/{video_id}/{filename}
```

## IA

Endpoints:

```http
GET /ai/status
GET /ai/models
POST /ai/test
GET /config/status
```

Configura `.env` a partir de `.env.example`. No guardes API keys reales en archivos versionados.

## Despliegue manual en Vercel

Antes de desplegar manualmente, configura las variables de entorno desde el dashboard de Vercel:

```text
GEMINI_API_KEY
GEMINI_API_KEYS
INSFORGE_BASE_URL
INSFORGE_ANON_KEY
```

No escribas estos valores en el codigo ni en archivos versionados. El Preview/UI puede arrancar sin ellas, pero las pruebas reales con Gemini e InsForge necesitan esas variables activas en Vercel.

Nota operativa: el despliegue visual no certifica procesamiento pesado en serverless. FFmpeg, Whisper local, jobs largos, uploads grandes y Vault persistente requieren una fase posterior de arquitectura cloud.

### Alcance MVP en Vercel

El MVP cloud queda certificado para UI/API, diagnostico, Gemini Cloud, InsForge y jobs cortos. En Vercel, el Vault usa `/tmp/scriptdna-vault` como workspace temporal y los resultados que deban sobrevivir cold starts deben estar persistidos en InsForge.

Antes de pruebas humanas, ejecuta el runbook de produccion:

```bash
python3 backend/tools/live_preflight.py --base-url https://scriptdna-preview.vercel.app
```

La matriz manual completa esta en `LIVE_TEST_RUNBOOK.md`.

Quedan fuera de esta certificacion: videos largos, descargas bloqueadas por YouTube/Instagram, uploads grandes, audio descargable durable y procesos que excedan `maxDuration: 60`. Para esos casos, la siguiente fase debe mover el procesamiento pesado a un worker o servicio durable y dejar Vercel como UI/API liviana.

Instagram en Vercel: si el reel/video requiere login, cookies o dispara rate-limit, la app no intenta usar credenciales de Instagram. Descarga el archivo en tu dispositivo y procésalo con la opción `Arrastra video`.

Para validar localmente el mismo runtime declarado para despliegue, usa Python 3.12. Si `backend/venv/bin/python --version` muestra Python 3.9, recrea el entorno antes de tomar los checks locales como equivalentes al deploy.

Si `/ai/test` devuelve `PERMISSION_DENIED` o indica que una API key fue reportada como filtrada, rota esa key en Vercel. La app intenta saltar a la siguiente llave configurada en `GEMINI_API_KEYS`, pero si todas estan bloqueadas el MVP no puede ejecutar Gemini hasta reemplazarlas.

## Control local de Ollama

La pestana `IA` permite monitorear, encender, apagar y reiniciar Ollama desde la web local. En macOS la app intenta usar el servicio `launchd` `com.ollama.ollama`; si no esta disponible, puede iniciar `ollama serve` como proceso local controlado.

Endpoints:

```http
GET /ollama/status
POST /ollama/start
POST /ollama/stop
POST /ollama/restart
```

Apagar Ollama libera CPU/RAM/GPU local. Si hay jobs activos usando `ai_provider="ollama"`, la app bloquea `stop` y `restart` para evitar cortar un analisis en curso.

## Seguridad

No guardes API keys ni secretos en codigo. Usa `.env` o variables de entorno. Si Gemini no esta configurado o falla, AD MediaSolution Studio puede usar Ollama local o generar una base de fallback para no cortar el flujo operativo.
