# AD MediaSolution Studio - Runbook De Pruebas En Vivo

## Objetivo
Garantizar pruebas humanas sin errores conocidos. Todo flujo debe terminar en resultado esperado, mensaje operativo claro o criterio No-Go.

## Produccion
- URL: `https://scriptdna-preview.vercel.app`
- Ambiente: Production
- No usar Preview para validacion humana final.
- No pegar secretos, cookies, API keys ni credenciales en prompts, reportes o capturas.

## Preflight Automatico
Ejecutar antes de invitar usuarios humanos:

```bash
python3 backend/tools/live_preflight.py --base-url https://scriptdna-preview.vercel.app
```

Resultado esperado:
- `PASS /app`
- `PASS /static/app.css`
- `PASS /static/app.js`
- `PASS /config/status`
- `PASS /ai/status`
- `PASS /diagnostic`
- `PASS /vault/brands`
- `PASS /ai/test`
- `PASS /jobs/process-url instagram guardrail`

Si aparece cualquier `FAIL`, detener pruebas humanas y corregir primero.

## Matriz Manual

### A. Carga Inicial
1. Abrir `https://scriptdna-preview.vercel.app/app`.
2. Confirmar que no hay pantalla en blanco.
3. Confirmar que sidebar, status cards y formulario aparecen.
4. Resultado esperado: UI cargada y estado cloud visible.

### B. IA
1. Abrir pestaña `Pipeline cloud`.
2. Ejecutar `Probar conexión`.
3. Resultado esperado: respuesta Gemini exitosa.
4. Si falla, detener pruebas de procesamiento.

### C. Instagram URL
1. Ir a `Procesar`.
2. Pegar una URL de Instagram.
3. Resultado esperado: aviso inmediato indicando descargar el archivo y usar `Arrastra video`.
4. No debe crearse job largo.
5. No considerar esto un fallo; es el comportamiento esperado.

### D. Upload Corto
1. Usar archivo `.mp4`, `.mov`, `.mp3` o `.wav`.
2. Tamano maximo recomendado: 25 MB.
3. Duracion maxima recomendada: 60 segundos.
4. Completar marca e ID con nombres simples, por ejemplo `Human QA` y `smoke-YYYYMMDD-HHMM`.
5. Seleccionar `Arrastra video` y subir archivo.
6. Resultado esperado: job creado, polling visible y estado final `completed` o error accionable no tecnico.
7. Si el job no cambia de estado por mas de 90 segundos, detener y registrar.

### E. Vault
1. Abrir pestaña `Vault`.
2. Seleccionar la marca usada en Upload Corto.
3. Seleccionar el video.
4. Resultado esperado: pieza visible, con guion/metadata/outputs disponibles cuando correspondan.

### F. Outputs Creativos
1. Si el video tiene analisis completo, abrir `Outputs creativos`.
2. Ejecutar o abrir `Generar pack`.
3. Resultado esperado: pack visible o mensaje claro de requisito faltante.

## Criterios No-Go
Detener pruebas humanas si ocurre cualquiera:
- `/app` no carga.
- Assets CSS/JS devuelven 404.
- Gemini no esta disponible.
- `keys_available=0`.
- InsForge no esta configurado.
- `diagnostic.gemini.live_test=false`.
- Error tecnico crudo visible para el usuario.
- Job sin cambio de estado por mas de 90 segundos.
- Instagram URL intenta procesar en vez de mostrar guardrail.

## Registro Minimo De Incidentes
Copiar solo esto:
- Fecha/hora.
- URL exacta.
- Navegador.
- Paso del runbook.
- Texto exacto del error.
- Endpoint si aplica.
- Payload minimo sin secretos.
- Captura si no contiene datos sensibles.

## Orden Para Modelos Pequenos
1. Ejecutar preflight automatico.
2. Si hay `FAIL`, detener y reportar.
3. Abrir UI.
4. Probar Gemini.
5. Probar guardrail Instagram.
6. Probar upload corto.
7. Revisar Vault.
8. Revisar Creative Pack solo si existe analisis.
9. No improvisar cookies, credenciales ni videos largos.
