# AD MediaSolution Studio - Plan De Ajustes Visuales Locales

## Resumen
Levantar la aplicacion en entorno local, revisar la interfaz actual y preparar una fase de cambios visuales guiada por feedback humano.

## Protocolo Operativo
<vibe_coding_protocol>
  <reasoning_before_action>
    Este archivo registra el plan antes de editar archivos de la aplicacion.
    La exploracion inicial y el arranque local se usan para entender el estado real de la UI.
    Los cambios visuales se implementaran solo despues de aprobacion explicita del vibe.
  </reasoning_before_action>

  <xml_guardrails>
    Las reglas criticas se mantienen envueltas en etiquetas XML claras.
    Si durante la sesion aparecen nuevas guardrails, se agregaran preservando esta jerarquia XML.
  </xml_guardrails>

  <educational_feedback>
    Cada bloque tecnico importante explicara que se hara, por que se hace y que beneficio aporta a la operacion.
    La explicacion sera breve, enfocada en decisiones utiles de producto y experiencia visual.
  </educational_feedback>

  <atomicity>
    El trabajo se organiza en fases: ejecutar local, observar la UI, implementar una tanda acotada de cambios visuales y validar en navegador.
    La validacion visual se tratara como fase separada despues de editar CSS/HTML/JS.
  </atomicity>

  <security>
    No se escribiran tokens, API keys, cookies ni secretos en codigo, prompts persistentes o archivos versionados.
    Cualquier configuracion sensible seguira viviendo en .env o variables de entorno.
  </security>
</vibe_coding_protocol>

## Fases
- Ejecutar la app localmente en `http://127.0.0.1:8000/app`.
- Inspeccionar la UI actual y detectar los archivos visuales relevantes: `backend/static/app.html`, `backend/static/app.css` y `backend/static/app.js`.
- Esperar feedback y aprobacion explicita del vibe sobre los cambios visuales deseados.
- Implementar los cambios aprobados en una tanda pequena y coherente.
- Validar localmente con navegador y checks automaticos disponibles.

## Beneficio Operativo
Trabajar contra la app real evita cambios esteticos a ciegas y permite validar rapido si la interfaz queda mas clara, mas usable y mas alineada con el flujo de procesamiento de guiones.

## Validacion Prevista
- Confirmar que la app carga en local.
- Revisar que no haya errores visibles de layout en desktop.
- Si se editan archivos frontend, verificar en navegador que los controles principales sigan accesibles.
