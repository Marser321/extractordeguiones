from pathlib import Path
import json
from datetime import datetime
from typing import Optional

try:
    from services.ai_provider_service import ai_provider_service
    from services.context_audit_service import context_audit_service
    from services.vault_service import vault_service
    from services.training_service import training_service
except ModuleNotFoundError:
    from backend.services.ai_provider_service import ai_provider_service
    from backend.services.context_audit_service import context_audit_service
    from backend.services.vault_service import vault_service
    from backend.services.training_service import training_service


class AnalysisService:
    PROMPT_VERSION = "scriptdna-business-v3"

    def analyze_script(
        self,
        video_path: Path,
        brand_name: str,
        video_id: str,
        script_text: str,
        ai_provider: str = "ollama",
        ai_model: Optional[str] = None,
        analysis_modules: Optional[list] = None,
        fallback_provider: str = "ollama",
    ) -> dict:
        modules = analysis_modules or self.default_modules()
        brand_profile = vault_service.get_brand_profile(brand_name)
        analysis_dir = vault_service.create_analysis_dir(brand_name, video_id)

        brand_path = vault_service.create_brand_structure(brand_name)
        patterns = vault_service.read_json(brand_path / "Analisis" / "patrones.json") or {}
        visual_context = vault_service.read_json(analysis_dir / "analisis_visual.json") or {}
        context_inputs = self._context_inputs(script_text, brand_profile, patterns, visual_context)

        prompt = self._build_business_prompt(brand_name, video_id, script_text, brand_profile, modules, patterns, visual_context)
        try:
            analysis = ai_provider_service.generate_json(
                prompt=prompt,
                provider=ai_provider,
                model=ai_model,
                fallback_provider=fallback_provider,
            )
            generation_mode = "ai"
        except Exception as error:
            analysis = self._fallback_analysis(brand_name, video_id, script_text, brand_profile, str(error))
            generation_mode = "local_fallback"

        analysis = self._repair_analysis_quality(analysis, brand_name, video_id, script_text, brand_profile, visual_context)
        analysis.setdefault("_prompt_version", self.PROMPT_VERSION)
        analysis.setdefault("_context_inputs", context_inputs)
        generated_files = self._write_outputs(analysis_dir, analysis)
        visual_status = self._write_visual_placeholder(analysis_dir, video_path)
        retrospective = self._write_retrospective(analysis_dir, analysis, generation_mode)
        patterns = self._record_pattern_candidates(brand_name, video_id, analysis)
        vault_service.save_json(analysis_dir, "full_analysis.json", analysis)
        audit = context_audit_service.audit_video(brand_name, video_id, save=True)

        # Capacidad de Entrenamiento: Refinamiento Automático
        if audit and audit.get("overall_score", 0) < 6.8 and generation_mode == "ai":
            refinement_instructions = audit.get("refinement_instructions")
            if refinement_instructions:
                try:
                    analysis = self.refine_analysis(
                        analysis, refinement_instructions, prompt,
                        ai_provider, ai_model, fallback_provider
                    )
                    generation_mode = "ai_refined"
                    # Guardar el análisis refinado y volver a auditar
                    vault_service.save_json(analysis_dir, "full_analysis.json", analysis)
                    self._write_outputs(analysis_dir, analysis)
                    audit = context_audit_service.audit_video(brand_name, video_id, save=True)
                except Exception:
                    pass

        status = {
            "status": "completed",
            "generation_mode": generation_mode,
            "provider": analysis.get("_ai_provider", ai_provider),
            "model": analysis.get("_ai_model", ai_model or ai_provider_service.default_model_for(ai_provider)),
            "fallback_provider": fallback_provider,
            "prompt_version": self.PROMPT_VERSION,
            "context_inputs": context_inputs,
            "modules": modules,
            "generated_files": generated_files + [visual_status, retrospective],
            "patterns_updated": False,
            "pattern_candidates_recorded": True,
            "audit": audit or {},
            "patterns": patterns,
        }
        vault_service.save_json(analysis_dir, "analisis_estado.json", status)
        return status

    def default_modules(self) -> list:
        return [
            "summary",
            "hooks",
            "viral_moments",
            "narrative_structure",
            "reel_ideas",
            "ads",
            "creative_brief",
            "captions",
            "publishing_calendar",
            "visual_prompts",
            "retrospective",
        ]

    def _write_outputs(self, analysis_dir: Path, analysis: dict) -> list:
        generated = []
        generated.append(str(vault_service.save_file(analysis_dir, "resumen_ejecutivo.md", self._as_markdown(analysis.get("resumen_ejecutivo")))))
        generated.append(str(vault_service.save_json(analysis_dir, "hooks.json", self._as_list(analysis.get("hooks")))))
        generated.append(str(vault_service.save_json(analysis_dir, "momentos_virales.json", self._as_list(analysis.get("momentos_virales")))))
        generated.append(str(vault_service.save_json(analysis_dir, "estructura_narrativa.json", self._as_dict(analysis.get("estructura_narrativa")))))
        generated.append(str(vault_service.save_json(analysis_dir, "ideas_reels.json", self._as_list(analysis.get("ideas_reels")))))
        generated.append(str(vault_service.save_json(analysis_dir, "ads.json", self._as_list(analysis.get("ads")))))
        generated.append(str(vault_service.save_file(analysis_dir, "brief_creativo.md", self._as_markdown(analysis.get("brief_creativo")))))
        generated.append(str(vault_service.save_json(analysis_dir, "captions.json", self._as_list(analysis.get("captions")))))
        generated.append(str(vault_service.save_json(analysis_dir, "calendario_publicacion.json", self._as_list(analysis.get("calendario_publicacion")))))
        generated.append(str(vault_service.save_json(analysis_dir, "prompts_visuales.json", self._as_list(analysis.get("prompts_visuales")))))
        generated.append(str(vault_service.save_json(analysis_dir, "prompt_base_marca.json", self._as_dict(analysis.get("prompt_base_marca")))))
        return generated

    def _write_visual_placeholder(self, analysis_dir: Path, video_path: Path) -> str:
        file_path = analysis_dir / "analisis_visual.json"
        if file_path.exists():
            existing = vault_service.read_json(file_path)
            if existing and existing.get("status") != "pending_visual_extraction":
                return str(file_path)

        original_dir = video_path / "original_video"
        source_files = [str(path) for path in original_dir.iterdir() if path.is_file()] if original_dir.exists() else []
        payload = {
            "status": "pending_visual_extraction",
            "source_files": source_files,
            "notes": "La extracción de frames/OCR se implementa como siguiente capa; este archivo reserva el contrato de análisis visual.",
            "frame_samples": [],
            "ocr_text": [],
            "shot_types": [],
            "editing_notes": [],
        }
        return str(vault_service.save_json(analysis_dir, "analisis_visual.json", payload))

    def _write_retrospective(self, analysis_dir: Path, analysis: dict, generation_mode: str) -> str:
        payload = self._as_dict(analysis.get("retrospectiva"))
        payload.setdefault("generation_mode", generation_mode)
        payload.setdefault("que_funciono", [])
        payload.setdefault("que_falto", [])
        payload.setdefault("siguiente_mejora", "Comparar este video contra futuros videos de la misma marca.")
        return str(vault_service.save_json(analysis_dir, "retrospectiva.json", payload))

    def _context_inputs(self, script_text: str, brand_profile: dict, patterns: dict, visual_context: dict) -> dict:
        visual_status = visual_context.get("status") if isinstance(visual_context, dict) else None
        return {
            "prompt_version": self.PROMPT_VERSION,
            "script_chars": len(script_text or ""),
            "script_truncated": len(script_text or "") > 18000,
            "brand_profile_fields": sorted([key for key, value in brand_profile.items() if value not in (None, "", [], {})]),
            "historical_pattern_counts": {
                key: len(value) for key, value in (patterns or {}).items() if isinstance(value, list)
            },
            "visual_context_available": bool(visual_context) and visual_status != "pending_visual_extraction",
            "visual_context_status": visual_status or ("available" if visual_context else "missing"),
        }

    def _record_pattern_candidates(self, brand_name: str, video_id: str, analysis: dict) -> dict:
        hooks = [item.get("hook") for item in self._as_list(analysis.get("hooks")) if isinstance(item, dict)]
        structures = self._as_dict(analysis.get("estructura_narrativa")).get("patron", [])
        angles = [item.get("angulo") or item.get("concepto") for item in self._as_list(analysis.get("ads")) if isinstance(item, dict)]
        style_rules = self._as_list(self._as_dict(analysis.get("prompt_base_marca")).get("do"))
        return vault_service.update_brand_patterns(brand_name, {
            "hooks_frecuentes": hooks[:8],
            "estructuras_ganadoras": structures if isinstance(structures, list) else [structures],
            "angulos_de_venta": angles[:8],
            "reglas_de_estilo": style_rules[:8],
        }, source_video_id=video_id, prompt_version=self.PROMPT_VERSION, promote=False)

    def _repair_analysis_quality(
        self,
        analysis: dict,
        brand_name: str,
        video_id: str,
        script_text: str,
        brand_profile: dict,
        visual_context: dict,
    ) -> dict:
        if not isinstance(analysis, dict):
            analysis = {}

        bad_markers = [
            "razonamiento psicologico detras del hook",
            "reel|short|ad|post",
            "thumbnail|ad|post|story",
            "duracion_sugerida",
            "texto disruptivo",
            "texto detallado",
            "regla",
        ]
        flat = json.dumps(analysis, ensure_ascii=False).lower()
        needs_repair = all(marker in flat for marker in bad_markers) # Change to 'all' or more specific check
        # Better check: if AI returns EXACTLY the placeholder text for most keys
        placeholders_found = 0
        for marker in bad_markers:
            if marker in flat:
                placeholders_found += 1
        
        needs_repair = placeholders_found >= 3 # Trigger repair only if 3 or more placeholders are found
        needs_repair = needs_repair or len(self._as_list(analysis.get("hooks"))) < 3
        needs_repair = needs_repair or len(self._as_list(analysis.get("prompts_visuales"))) < 4
        needs_repair = needs_repair or len(self._as_list(analysis.get("ads"))) < 2
        if not needs_repair:
            analysis.setdefault("_quality_repair", {"applied": False})
            return analysis

        repair = self._deterministic_quality_pack(brand_name, video_id, script_text, brand_profile, visual_context)
        for key, value in repair.items():
            current = analysis.get(key)
            if key in {"hooks", "momentos_virales", "ideas_reels", "ads", "captions", "calendario_publicacion", "prompts_visuales"}:
                if len(self._as_list(current)) < len(value) or self._contains_placeholder(current):
                    analysis[key] = value
            elif key in {"estructura_narrativa", "prompt_base_marca", "retrospectiva"}:
                if not self._as_dict(current) or self._contains_placeholder(current):
                    analysis[key] = value
            elif key in {"resumen_ejecutivo", "brief_creativo"}:
                if not current or self._contains_placeholder(current):
                    analysis[key] = value

        analysis["_quality_repair"] = {
            "applied": True,
            "reason": "Se detectaron placeholders, schema copiado o baja densidad de piezas.",
            "source": "script_visual_brand_deterministic_repair",
        }
        return analysis

    def _deterministic_quality_pack(self, brand_name: str, video_id: str, script_text: str, brand_profile: dict, visual_context: dict) -> dict:
        clean_script = " ".join((script_text or "").split())
        excerpt = clean_script[:420] or "El video no contiene suficiente texto transcrito."
        hook_core = self._script_hook(clean_script)
        cta = brand_profile.get("cta") or "Reserva tu lugar"
        audience = brand_profile.get("audience") or "emprendedores y equipos que buscan crecer con más claridad"
        tone = brand_profile.get("tone") or "directo, estratégico y accionable"
        visual_summary = self._visual_summary(visual_context)
        brand_style = brand_profile.get("visual_style") or visual_context.get("estilo_visual") or "visual claro, humano y orientado a performance"
        offer = brand_profile.get("offer") or "una propuesta para convertir atención en acción"

        return {
            "resumen_ejecutivo": (
                f"# Resumen ejecutivo\n\n"
                f"El video `{video_id}` abre una oportunidad de performance para `{brand_name}`: usar una pregunta económica concreta como filtro de intención y luego llevar a la audiencia hacia una decisión clara.\n\n"
                f"**Insight lateral:** el contenido no vende solo una solución; vende el salto mental entre mirar un negocio como gasto y mirarlo como sistema de retorno.\n\n"
                f"**Audiencia:** {audience}.\n\n"
                f"**Evidencia del guion:** {excerpt}\n\n"
                f"**Contexto visual:** {visual_summary}\n\n"
                f"**CTA operativo:** {cta}.\n"
            ),
            "hooks": [
                {
                    "hook": hook_core,
                    "uso": "reel",
                    "rationale": "Abre con una pregunta de dinero específica que fuerza al espectador a compararse con el escenario planteado.",
                },
                {
                    "hook": "¿Invertirías 3.000 para construir una vía a 30.000 al mes?",
                    "uso": "ad",
                    "rationale": "Convierte la promesa en una tensión riesgo-retorno, útil para filtrar leads con intención real.",
                },
                {
                    "hook": "El negocio no es el trámite: es el sistema que convierte demanda en ventas.",
                    "uso": "post",
                    "rationale": "Mueve la conversación de servicio puntual a mecanismo de crecimiento, más defendible para pauta.",
                },
                {
                    "hook": "Si el margen existe, el cuello de botella no es la idea: es capturar y cerrar la demanda.",
                    "uso": "short",
                    "rationale": "Introduce pensamiento lateral y prepara la necesidad de CRM, masterclass o sistema comercial.",
                },
            ],
            "momentos_virales": [
                {
                    "titulo": "Pregunta de facturación",
                    "descripcion": "Abrir con el desafío de facturar 30.000 dólares al mes y pedir al espectador que elija el negocio más rápido.",
                    "duracion_sugerida": "0-12s",
                    "motivo_retencion": "La cifra concreta y la pregunta competitiva generan curiosidad inmediata.",
                },
                {
                    "titulo": "Comparación inversión-retorno",
                    "descripcion": "Contrastar invertir 3.000 con la posibilidad de generar 30.000 para instalar la tensión principal.",
                    "duracion_sugerida": "12-28s",
                    "motivo_retencion": "El espectador se queda para entender si la relación riesgo-retorno hace sentido.",
                },
                {
                    "titulo": "Sistema de cierre",
                    "descripcion": "Presentar CRM, seguimiento o masterclass como mecanismo que convierte el interés en operación.",
                    "duracion_sugerida": "28-55s",
                    "motivo_retencion": "Pasa de promesa a proceso, elevando credibilidad.",
                },
            ],
            "estructura_narrativa": {
                "patron": ["pregunta economica", "tension riesgo-retorno", "mecanismo de sistema", "cta a masterclass"],
                "notas": "La curva de retención depende de mantener la cifra visible, explicar el mecanismo y cerrar con una acción única.",
            },
            "ideas_reels": [
                {
                    "titulo": "La pregunta de los 30K",
                    "estructura": "Texto grande con la pregunta, corte al orador, tres negocios posibles, CTA a comentar o reservar.",
                    "cta": cta,
                    "insight_lateral": "El reel funciona como test de mercado: quien responde ya está imaginando ROI.",
                },
                {
                    "titulo": "3K contra 30K",
                    "estructura": "Pantalla dividida inversión/retorno, objeción rápida, explicación del sistema, CTA.",
                    "cta": cta,
                    "insight_lateral": "La pieza transforma una compra en apuesta racional de negocio.",
                },
                {
                    "titulo": "El CRM invisible",
                    "estructura": "Hook sobre leads perdidos, ejemplo del proceso, visual de pipeline, invitación a masterclass.",
                    "cta": cta,
                    "insight_lateral": "Vende infraestructura comercial sin hablar como software genérico.",
                },
            ],
            "ads": [
                {
                    "concepto": "Reto de facturación mensual",
                    "angulo": "aspiración cuantificada",
                    "copy": f"{hook_core} Si quieres entender el sistema detrás de esa respuesta, este es el siguiente paso.",
                    "cta": cta,
                },
                {
                    "concepto": "Inversión con lógica de retorno",
                    "angulo": "riesgo calculado",
                    "copy": "No se trata de gastar en marketing. Se trata de construir una ruta medible entre atención, seguimiento y cierre.",
                    "cta": cta,
                },
                {
                    "concepto": "Masterclass como filtro",
                    "angulo": "autoridad práctica",
                    "copy": "Mira el proceso completo antes de invertir tiempo o dinero en otro canal que no sabes medir.",
                    "cta": cta,
                },
            ],
            "brief_creativo": (
                f"# Brief creativo\n\n"
                f"Objetivo: transformar el reel en piezas de performance que expliquen una oportunidad económica y lleven a una acción concreta.\n\n"
                f"Audiencia: {audience}.\n\n"
                f"Tono: {tone}.\n\n"
                f"Mensaje central: {offer}.\n\n"
                f"Dirección visual: {brand_style}. Usar la presencia del orador, fondo natural y texto grande para cifras clave.\n\n"
                f"Entregables: reel vertical, thumbnail, adset Meta, carrusel educativo y story con CTA.\n"
            ),
            "captions": [
                {"plataforma": "Instagram", "caption": f"{hook_core}\n\nLa respuesta no está solo en el negocio. Está en el sistema que captura demanda y la convierte en ventas.\n\n{cta}", "hashtags": ["#negocios", "#marketing", "#ventas"]},
                {"plataforma": "TikTok", "caption": "La pregunta no es cuánto cuesta empezar. Es qué sistema puede justificar el retorno.", "hashtags": ["#emprendedores", "#negociosonline"]},
                {"plataforma": "LinkedIn", "caption": "Una buena pieza de performance no empieza con una promesa; empieza con una tensión económica que el mercado reconoce.", "hashtags": ["#performance", "#growth"]},
            ],
            "calendario_publicacion": [
                {"dia": "Día 1", "pieza": "Reel pregunta 30K", "objetivo": "Capturar atención y comentarios cualificados."},
                {"dia": "Día 2", "pieza": "Carrusel inversión vs retorno", "objetivo": "Educar y guardar."},
                {"dia": "Día 3", "pieza": "Adset masterclass", "objetivo": "Generar reservas o leads."},
                {"dia": "Día 4", "pieza": "Story con encuesta", "objetivo": "Medir objeciones y activar DM."},
            ],
            "prompts_visuales": [
                {
                    "uso": "reel cover",
                    "prompt": f"Portada vertical 9:16 para {brand_name}, orador masculino con gafas en entorno exterior verde desenfocado, texto grande: '¿30K al mes?', composición con rostro a un tercio, contraste alto, estética {brand_style}, espacio seguro para subtítulo y CTA.",
                    "negative_prompt": "texto ilegible, cifras pequeñas, promesas exageradas, fondo saturado, rostro distorsionado",
                },
                {
                    "uso": "meta ad",
                    "prompt": f"Creativo 4:5 de performance para explicar inversión vs retorno, visual central con orador gesticulando, overlays '3K inversión' y '30K objetivo', fondo natural profesional, jerarquía clara, CTA: {cta}.",
                    "negative_prompt": "gráficos financieros falsos, lujo genérico, billetes irreales, exceso de texto",
                },
                {
                    "uso": "thumbnail",
                    "prompt": "Thumbnail 16:9 con primer plano del orador, fondo verde con bokeh, expresión de pregunta, copy grande '¿Qué negocio escala más rápido?', flecha sutil hacia cifra 30K, estilo nítido y creíble.",
                    "negative_prompt": "clickbait confuso, texto cortado, demasiados iconos",
                },
                {
                    "uso": "carousel",
                    "prompt": "Carrusel 4:5 educativo, slide 1 pregunta 30K, slide 2 inversión 3K, slide 3 sistema CRM, slide 4 masterclass, usar paleta sobria, tipografía pesada, composición editorial limpia.",
                    "negative_prompt": "plantilla genérica, saturación excesiva, layouts desordenados",
                },
            ],
            "prompt_base_marca": {
                "brand_name": brand_name,
                "tone": tone,
                "visual_direction": brand_style,
                "do": ["Usar cifras concretas como ancla", "Mantener al orador como prueba humana", "Separar promesa, mecanismo y CTA"],
                "dont": ["Inventar resultados garantizados", "Ocultar que la pieza depende de un sistema comercial", "Usar copies genéricos de motivación"],
            },
            "retrospectiva": {
                "que_funciono": ["La pregunta económica crea tensión inmediata.", "El contexto visual humano sostiene credibilidad."],
                "que_falto": ["Validar si la audiencia reconoce el caso de trámites migratorios como oportunidad prioritaria.", "Medir qué CTA convierte mejor: masterclass, reserva o DM."],
                "siguiente_mejora": "Crear 3 variantes de adset separando aspiración, objeción de inversión y mecanismo CRM.",
            },
        }

    def _contains_placeholder(self, value) -> bool:
        text = json.dumps(value, ensure_ascii=False).lower() if not isinstance(value, str) else value.lower()
        markers = [
            "razonamiento psicologico detras del hook",
            "reel|short|ad|post",
            "thumbnail|ad|post|story",
            "texto disruptivo",
            "texto detallado",
            '"regla"',
        ]
        return any(marker in text for marker in markers)

    def _script_hook(self, script_text: str) -> str:
        if "30.000" in script_text or "30000" in script_text:
            return "¿Con qué negocio facturarías más rápido 30.000 dólares por mes?"
        sentence = (script_text or "").split(".")[0].strip()
        return sentence[:110] if sentence else "La pregunta que revela si tu contenido puede vender"

    def _visual_summary(self, visual_context: dict) -> str:
        if not isinstance(visual_context, dict) or not visual_context:
            return "Contexto visual no disponible; usar supuestos marcados."
        if visual_context.get("status") == "pending_visual_extraction":
            return "Contexto visual pendiente; no inventar escenas ni objetos."
        elements = visual_context.get("elementos_clave") or []
        scenario = visual_context.get("escenario") or visual_context.get("estilo_visual") or "contexto visual disponible"
        if elements:
            return f"{scenario} Elementos clave: {', '.join([str(item) for item in elements[:3]])}."
        return str(scenario)

    def _build_business_prompt(
        self,
        brand_name: str,
        video_id: str,
        script_text: str,
        brand_profile: dict,
        modules: list,
        patterns: dict,
        visual_context: dict,
    ) -> str:
        patterns_str = json.dumps(patterns or {}, ensure_ascii=False, indent=2)
        brand_profile_str = json.dumps(brand_profile or {}, ensure_ascii=False, indent=2)
        visual_str = json.dumps(visual_context or {}, ensure_ascii=False, indent=2)
        modules_str = json.dumps(modules or [], ensure_ascii=False)
        negative_memory = training_service.get_negative_memory(brand_name)
        negative_memory_str = json.dumps(negative_memory, ensure_ascii=False, indent=2)
        
        # Cargar Sabiduría de Marca (Reglas de Oro y Barreras)
        brand_path = vault_service.create_brand_structure(brand_name)
        wisdom = vault_service.read_json(brand_path / "Analisis" / "sabiduria_marca.json") or {}
        wisdom_str = json.dumps(wisdom, ensure_ascii=False, indent=2)

        transcript = (script_text or "")[:18000]
        current_date = datetime.utcnow().date().isoformat()

        return f"""
<scriptdna_prompt version="{self.PROMPT_VERSION}">
  <role>
    Eres ScriptDNA Pro, un estratega creativo experto en pensamiento lateral, auditoria de contenido y marketing de performance.
    Tu mision es convertir un guion y su contexto de marca en activos accionables, especificos y verificables.
  </role>

  <task>
    Analiza el guion del video `{video_id}` para la marca `{brand_name}`.
    Produce un paquete creativo en espanol que respete la marca, use evidencia del guion y aporte conexiones no obvias.
  </task>

  <available_context>
    <date_utc>{current_date}</date_utc>
    <brand_profile>{brand_profile_str}</brand_profile>
    <marketing_logic>
      No te limites a resumir. Usa PENSAMIENTO LATERAL para encontrar angulos no obvios.
      Busca la 'Tension de Marca' y la 'Gran Idea' disruptiva.
      Todo el copy generado debe ser en ESPAÑOL NEUTRO, experto y persuasivo.
    </marketing_logic>
    <brand_wisdom>{wisdom_str}</brand_wisdom>
    <historical_memory>{patterns_str}</historical_memory>
    <visual_context>{visual_str}</visual_context>
    <requested_modules>{modules_str}</requested_modules>
    <negative_memory>
      IMPORTANTE: Los siguientes patrones han fallado en auditorias anteriores o no cumplen con la calidad esperada. EVITALOS:
      {negative_memory_str}
    </negative_memory>
  </available_context>

    <quality_rubric>
    - Pensamiento lateral (CRÍTICO): No te limites a resumir. Identifica tensiones, paradojas, simbolos, psicologia del espectador o conexiones culturales no evidentes.
    - COHERENCIA VISUAL-NARRATIVA (NUEVO): Cada gancho (hook), ad o idea visual DEBE referenciar elementos detectados en los frames (ej: 'Aprovecha el fondo minimalista que se ve al inicio...', 'Usa el gesto de autoridad del orador en el segundo 15...'). No generes piezas que podrian aplicarse a cualquier video genérico.
    - Fidelidad: cada recomendacion debe poder rastrearse al guion, perfil de marca o contexto visual.
    - Especificidad: evita hooks genericos; cada pieza debe ser concreta, accionable y util para marketing.
    - Visual: si el contexto visual esta disponible, es OBLIGATORIO integrarlo en las descripciones y rationale de los hooks.
  </quality_rubric>

  <output_schema>
    Devuelve exclusivamente JSON valido con estas claves exactas:
    {{
      "resumen_ejecutivo": "Markdown con tema, insight lateral, objetivo, tono, oportunidad de negocio y supuestos si aplica.",
      "hooks": [{{"hook": "texto disruptivo", "uso": "reel|short|ad|post", "rationale": "razonamiento psicologico detras del hook"}}],
      "momentos_virales": [{{"titulo": "texto", "descripcion": "texto", "duracion_sugerida": "15-60s", "motivo_retencion": "por que este momento retiene"}}],
      "estructura_narrativa": {{"patron": ["apertura", "tension", "valor", "cta"], "notas": "analisis de curva de retencion"}},
      "ideas_reels": [{{"titulo": "texto", "estructura": "texto", "cta": "texto", "insight_lateral": "conexion no obvia"}}],
      "ads": [{{"concepto": "texto", "angulo": "texto", "copy": "texto", "cta": "texto"}}],
      "brief_creativo": "Markdown con objetivo, audiencia psicografica, mensaje central, entregables y direccion visual.",
      "captions": [{{"plataforma": "Instagram|TikTok|YouTube|LinkedIn", "caption": "texto", "hashtags": ["tag"]}}],
      "calendario_publicacion": [{{"dia": "Dia 1", "pieza": "texto", "objetivo": "texto"}}],
      "prompts_visuales": [{{"uso": "thumbnail|ad|post|story", "prompt": "prompt visual detallado y consistente con la evidencia", "negative_prompt": "que evitar"}}],
      "prompt_base_marca": {{"brand_name": "{brand_name}", "tone": "texto", "visual_direction": "texto", "do": ["regla"], "dont": ["regla"]}},
      "retrospectiva": {{"que_funciono": ["texto"], "que_falto": ["texto"], "siguiente_mejora": "sugerencia de evolucion"}}
    }}
  </output_schema>

  <constraints>
    - No inventes hechos no soportados por el guion, perfil de marca o contexto visual.
    - Si el guion es corto o ambiguo, genera activos igualmente, pero marca los supuestos.
    - Si el contexto visual dice `pending_visual_extraction`, no describas escenas, colores, personas u objetos como si estuvieran verificados.
    - No incluyas claves fuera del schema salvo metadata interna iniciada con `_` si fuera estrictamente necesario.
    - Escribe en espanol claro, experto, directo y accionable.
  </constraints>

  <source_transcript>
{transcript}
  </source_transcript>
</scriptdna_prompt>
""".strip()

    def _fallback_analysis(self, brand_name: str, video_id: str, script_text: str, brand_profile: dict, reason: str) -> dict:
        excerpt = script_text[:500].strip() or "Guion vacío o sin habla detectada."
        cta = brand_profile.get("cta") or "Conocer más"
        return {
            "_ai_provider": "local_fallback",
            "_ai_model": "deterministic",
            "resumen_ejecutivo": f"# Resumen ejecutivo\n\nNo se pudo usar el proveedor IA seleccionado: {reason}\n\nExtracto base:\n\n{excerpt}\n",
            "hooks": [
                {"hook": "Esto es lo que nadie te muestra del proceso.", "uso": "reel", "rationale": "Abre curiosidad y permite reutilizar el guion."},
                {"hook": "La idea principal en menos de un minuto.", "uso": "short", "rationale": "Promete síntesis y valor rápido."},
            ],
            "momentos_virales": [
                {"titulo": "Idea central", "descripcion": excerpt, "duracion_sugerida": "15-30s", "motivo_retencion": "Extrae el punto más directo disponible."}
            ],
            "estructura_narrativa": {"patron": ["hook", "contexto", "idea central", "cta"], "notas": "Estructura fallback generada sin IA externa."},
            "ideas_reels": [{"titulo": "Recorte principal", "estructura": "Hook + extracto + CTA", "cta": cta}],
            "ads": [{"concepto": "Mensaje directo", "angulo": "claridad", "copy": excerpt, "cta": cta}],
            "brief_creativo": f"# Brief creativo\n\nObjetivo: reutilizar el contenido base.\n\nAudiencia: {brand_profile.get('audience')}\n\nCTA: {cta}\n",
            "captions": [{"plataforma": "Instagram", "caption": excerpt, "hashtags": ["#contenido", "#marca"]}],
            "calendario_publicacion": [{"dia": "Día 1", "pieza": "Post resumen", "objetivo": "Validar interés inicial"}],
            "prompts_visuales": [{"uso": "post", "prompt": f"Imagen limpia y moderna para {brand_name}, basada en: {excerpt}", "negative_prompt": "texto ilegible, exceso de elementos"}],
            "prompt_base_marca": {"brand_name": brand_name, "tone": brand_profile.get("tone"), "visual_direction": brand_profile.get("visual_style"), "do": ["Mantener claridad"], "dont": ["Prometer resultados no verificables"]},
            "retrospectiva": {"que_funciono": ["Se generó una base operativa"], "que_falto": ["Proveedor IA funcional"], "siguiente_mejora": "Configurar Gemini o verificar modelo Ollama."},
        }

    def _as_markdown(self, value) -> str:
        if isinstance(value, str):
            return value.strip() + "\n"
        return str(value or "").strip() + "\n"

    def _as_list(self, value) -> list:
        return value if isinstance(value, list) else []

    def _as_dict(self, value) -> dict:
        return value if isinstance(value, dict) else {}

    def refine_analysis(
        self,
        original_analysis: dict,
        instructions: str,
        original_prompt: str,
        provider: str,
        model: Optional[str],
        fallback: str
    ) -> dict:
        """Realiza un segundo pase de IA para corregir errores detectados por la auditoría."""
        refinement_prompt = f"""
{original_prompt}

<refinement_pass>
  {instructions}
  
  TOMA EL JSON ANTERIOR Y MEJORALO. Devuelve unicamente el JSON corregido.
  JSON ANTERIOR: {json.dumps(original_analysis, ensure_ascii=False)}
</refinement_pass>
"""
        return ai_provider_service.generate_json(
            prompt=refinement_prompt,
            provider=provider,
            model=model,
            fallback_provider=fallback
        )


analysis_service = AnalysisService()
