# ScriptDNA - Plan Open-Source-First Con Qwen Directo

## Resumen
La prioridad del MVP cambia a Qwen directo via Alibaba Cloud Model Studio/DashScope como motor principal. Hugging Face y fal quedan como capa open-source-first para modelos y media; OpenRouter queda como respaldo/comparacion; Gemini/OpenAI quedan opcionales; Ollama queda como ultima opcion local.

## Protocolo Operativo
<vibe_coding_protocol>
  <reasoning_before_action>
    Este archivo registra el plan antes de editar archivos de aplicacion o ejecutar cambios de implementacion.
    La implementacion priorizara Qwen directo para el core del MVP y solo usara proveedores secundarios cuando la tarea lo requiera.
    La aprobacion explicita del usuario en el mensaje "PLEASE IMPLEMENT THIS PLAN" se toma como aprobacion del vibe para continuar despues de registrar este plan.
  </reasoning_before_action>

  <xml_guardrails>
    Todas las reglas criticas se mantienen envueltas en etiquetas XML claras.
    Si se agregan guardrails durante la ejecucion, se preservara esta jerarquia para mantener prioridades visibles y auditables.
  </xml_guardrails>

  <educational_feedback>
    Cada bloque tecnico importante explicara que se hara, por que se hace y que beneficio aporta a negocio u operacion.
    La explicacion sera breve y enfocada en decisiones utiles: confiabilidad del MVP, calidad de modelos, velocidad de testeo, costos y experiencia de uso.
  </educational_feedback>

  <atomicity>
    El trabajo se organizara en fases: configuracion segura, providers, UI, docs/scripts y validacion.
    La validacion de navegador y smoke tests se tratara como fase separada despues de editar codigo.
  </atomicity>

  <security>
    No se escribiran tokens, API keys, cookies, PITs ni secretos equivalentes en codigo, prompts persistentes o archivos versionados.
    Los secretos seguiran viviendo en .env, variables de entorno o el gestor de secretos de la plataforma correspondiente.
    La UI solo mostrara estado, guias y nombres de variables; no guardara llaves.
  </security>
</vibe_coding_protocol>

## Cambios Clave
- Agregar configuracion segura para `DASHSCOPE_API_KEY`/`QWEN_API_KEY`, `QWEN_BASE_URL`, modelos Qwen por tarea, `HF_TOKEN` y `FAL_KEY`.
- Implementar provider `qwen` OpenAI-compatible para texto, JSON y vision/multimodal cuando el modelo lo soporte.
- Agregar providers `huggingface` y `fal` para disponibilidad, registry y media; fal sera la primera opcion para imagen/video cuando exista `FAL_KEY`.
- Reordenar fallback: `qwen` como principal, `huggingface`/`fal` segun tarea, `openrouter` como respaldo, `gemini`/`openai` opcionales y `ollama` como ultima opcion local.
- Actualizar UI para mostrar "Qwen API" como core requerido, "fal/Hugging Face" como media, "OpenRouter" como respaldo y "Ollama local" al final.
- Actualizar README, `.env.example`, preflight y scripts para probar `provider=qwen` primero.

## APIs E Interfaces
- `/ai/status` reportara `qwen`, `huggingface`, `fal`, `openrouter`, `gemini`, `openai` y `ollama`.
- `/ai/models` devolvera registry por tarea: rapido, calidad, deep, vision, imagen/video y fallback.
- `/ai/test` aceptara `{provider: "qwen", model, prompt}` y devolvera `{provider, model, response}`.
- Se mantendra compatibilidad con `/jobs/process-*`, `/jobs/analyze/*`, `/creative-pack/*`, `/vault/*` y parametros `ai_provider`/`ai_model`.
- No se tocara InsForge en esta fase salvo que sea imprescindible; si se toca, se consultara primero la documentacion InsForge via MCP si esta disponible.

## Validacion Prevista
- Compilar backend Python con `py_compile`.
- Validar frontend con `node --check backend/static/app.js`.
- Smoke con `TestClient`: `/app`, `/ai/status`, `/config/status`, `/ai/models` y `/ai/test`.
- Sin llaves reales, Qwen/HF/fal deben devolver estados claros de configuracion faltante sin romper UI ni flujo.
- Si existe `DASHSCOPE_API_KEY` o `QWEN_API_KEY`, ejecutar smoke real de `/ai/test` con Qwen.
- Si existe `FAL_KEY` o `HF_TOKEN`, validar estado y evitar pruebas costosas de media sin aprobacion explicita.
- Abrir `/app` en navegador local y verificar Qwen como principal, Ollama como ultima opcion y cero errores nuevos de consola.

## Beneficio Operativo
El MVP queda listo para operar con una key directa de Qwen y activar capacidades extra por llaves claras. Esto reduce dependencia de gateways, deja el costo mas visible, conserva fallback cloud/local y permite comparar calidad de modelos open-source-first sin rearmar la app.
