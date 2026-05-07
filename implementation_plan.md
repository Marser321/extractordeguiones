# AD MediaSolution - Pulido Visual De App

## Resumen
Rebrandear la experiencia visible de la app como **AD MediaSolution**, usando `Final.jpg` como fuente de logo, paleta y tono visual. ScriptDNA queda como etiqueta secundaria de producto interno.

## Protocolo Operativo
<vibe_coding_protocol>
  <reasoning_before_action>
    Este archivo registra el plan aprobado antes de editar la aplicacion.
    La solicitud actual aprueba implementar el plan, por lo que despues de registrar estas guardrails se puede mutar la implementacion local.
  </reasoning_before_action>

  <xml_guardrails>
    Las reglas criticas se mantienen envueltas en etiquetas XML claras.
    Se preserva la jerarquia XML para facilitar auditoria.
  </xml_guardrails>

  <educational_feedback>
    Se explicara cada bloque tecnico importante, por que se hace y que beneficio operativo aporta.
    La explicacion sera breve y no narrara comandos triviales.
  </educational_feedback>

  <atomicity>
    El trabajo se organiza en fases: assets de marca, shell UI, sistema visual, notas de despliegue y validacion.
    La validacion visual se trata como fase separada despues de los checks automaticos.
  </atomicity>

  <security>
    No se escribiran tokens, API keys ni secretos en codigo, prompts persistentes o archivos versionados.
    Las variables Gemini e InsForge deben configurarse manualmente en Vercel.
  </security>
</vibe_coding_protocol>

## Cambios Clave
- Crear assets reutilizables en `backend/static/brand/` desde `Final.jpg`.
- Rebrandear sidebar, titulo del navegador, microcopy y estados visibles como AD MediaSolution.
- Aplicar paleta `#81E7FF`, `#488EFF`, `#01327F`, `#2E3033`, `#F3FAFD`, `#FEFEFE`.
- Mantener ScriptDNA como subtitulo/producto secundario.
- Agregar notas de despliegue manual para `GEMINI_API_KEY`, `GEMINI_API_KEYS`, `INSFORGE_ANON_KEY` e `INSFORGE_BASE_URL`.

## Validacion
- `backend/venv/bin/python -m py_compile backend/main.py backend/core/config.py backend/services/*.py`
- `node --check backend/static/app.js`
- Import smoke con `PYTHONPATH=backend`.
- Verificacion visual de `/app` en navegador local.

## Supuestos
- No se ejecutara deploy automatico.
- `Final.jpg` es la fuente aprobada de identidad.
- La configuracion real de APIs se hara manualmente en Vercel.
- El pulido visual no certifica FFmpeg, Whisper, jobs largos, Vault persistente ni procesamiento pesado en serverless.
