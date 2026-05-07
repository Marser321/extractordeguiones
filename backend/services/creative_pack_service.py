import json
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from core.config import settings
    from services.ai_provider_service import ai_provider_service
    from services.vault_service import vault_service
    from services.creative_audit_service import creative_audit_service
except ModuleNotFoundError:
    from backend.core.config import settings
    from backend.services.ai_provider_service import ai_provider_service
    from backend.services.vault_service import vault_service
    from backend.services.creative_audit_service import creative_audit_service


class CreativePackService:
    PACK_VERSION = "scriptdna-creative-pack-v2"

    CHANNELS = [
        ("instagram", "Post/Reel/Story para Instagram", "4:5, 9:16"),
        ("tiktok", "TikTok/Reel vertical", "9:16"),
        ("youtube_shorts", "YouTube Shorts", "9:16"),
        ("youtube_thumbnail", "Thumbnail YouTube", "16:9"),
        ("linkedin", "Post profesional LinkedIn", "1.91:1, 4:5"),
        ("meta_ads", "Meta Ads feed/story", "1:1, 4:5, 9:16"),
        ("stories", "Story secuencial", "9:16"),
        ("carousel", "Carrusel educativo", "4:5"),
    ]

    ASSET_TYPES = [
        "adset visual",
        "hero image",
        "thumbnail",
        "product/service card",
        "quote card",
        "problem/solution card",
        "comparison card",
        "testimonial-style card",
        "reel cover",
    ]

    def generate_pack(
        self,
        brand_name: str,
        video_id: str,
        ai_provider: str = "gemini",
        ai_model: Optional[str] = None,
        fallback_provider: Optional[str] = None,
    ) -> dict:
        context = self._load_context(brand_name, video_id)
        prompt = self._build_prompt(context)
        generation_mode = "ai"
        if ai_provider == "local":
            pack = self._fallback_pack(context, "modo local determinístico")
            generation_mode = "local_fallback"
        else:
            try:
                pack = ai_provider_service.generate_json(
                    prompt=prompt,
                    provider=ai_provider,
                    model=ai_model,
                    fallback_provider=fallback_provider or settings.AI_FALLBACK_PROVIDER,
                )
            except Exception as error:
                pack = self._fallback_pack(context, str(error))
                generation_mode = "local_fallback"

        pack = self._normalize_pack(pack, context, generation_mode, ai_provider, ai_model)
        
        # Auditoría de Coherencia Transmedia
        print(f"[CreativeLab] Auditando coherencia transmedia...")
        audit = creative_audit_service.audit_pack(pack, context["analysis"])
        pack["audit"] = audit
        
        self._write_pack(context["creative_dir"], pack)
        return pack

    def read_pack(self, brand_name: str, video_id: str) -> dict:
        video_path = vault_service.get_video_path(brand_name, video_id)
        pack_path = video_path / "Analisis" / "CreativeLab" / "creative_pack.json"
        pack = vault_service.read_json(pack_path)
        if not pack:
            raise FileNotFoundError("No se encontró creative_pack.json para este video.")
        return pack

    def pack_paths(self, brand_name: str, video_id: str) -> dict:
        video_path = vault_service.get_video_path(brand_name, video_id)
        creative_dir = video_path / "Analisis" / "CreativeLab"
        return {
            "json": creative_dir / "creative_pack.json",
            "markdown": creative_dir / "creative_pack.md",
        }

    def _load_context(self, brand_name: str, video_id: str) -> dict:
        video_path = vault_service.get_video_path(brand_name, video_id)
        if not video_path.exists():
            raise FileNotFoundError("Video no encontrado en el Vault.")
        analysis_dir = video_path / "Analisis"
        creative_dir = analysis_dir / "CreativeLab"
        creative_dir.mkdir(parents=True, exist_ok=True)

        script_text = vault_service.read_file(video_path / "guion_original.txt") or ""
        if not script_text:
            raise FileNotFoundError("No hay guion para crear un pack creativo.")

        return {
            "brand_name": brand_name,
            "video_id": video_id,
            "video_path": video_path,
            "analysis_dir": analysis_dir,
            "creative_dir": creative_dir,
            "script_text": script_text,
            "brand_profile": vault_service.get_brand_profile(brand_name),
            "analysis": vault_service.read_json(analysis_dir / "full_analysis.json") or {},
            "visual_context": vault_service.read_json(analysis_dir / "analisis_visual.json") or {},
            "audit": vault_service.read_json(analysis_dir / "auditoria_contexto.json") or {},
            "hooks": vault_service.read_json(analysis_dir / "hooks.json") or [],
            "ads": vault_service.read_json(analysis_dir / "ads.json") or [],
            "captions": vault_service.read_json(analysis_dir / "captions.json") or [],
            "brief": vault_service.read_file(analysis_dir / "brief_creativo.md") or "",
            "brand_prompt": vault_service.read_json(analysis_dir / "prompt_base_marca.json") or {},
            "visual_prompts": vault_service.read_json(analysis_dir / "prompts_visuales.json") or [],
        }

    def _build_prompt(self, context: dict) -> str:
        payload = {
            "brand_name": context["brand_name"],
            "video_id": context["video_id"],
            "brand_profile": context["brand_profile"],
            "audit": context["audit"],
            "hooks": context["hooks"],
            "ads": context["ads"],
            "captions": context["captions"],
            "brief": context["brief"],
            "brand_prompt": context["brand_prompt"],
            "visual_context": context["visual_context"],
            "existing_visual_prompts": context["visual_prompts"],
            "script_excerpt": context["script_text"][:8000],
            "channels": [channel[0] for channel in self.CHANNELS],
            "asset_types": self.ASSET_TYPES,
        }
        return f"""
<scriptdna_creative_lab version="{self.PACK_VERSION}">
  <role>
    Eres un director creativo senior especializado en performance, prompts visuales, social content y adsets.
    Tu trabajo es extraer el maximo valor creativo de un video ya analizado.
  </role>

  <task>
    Genera un creative pack maduro para herramientas externas: Midjourney, Ideogram, Canva, Meta Ads, TikTok, Reels, Shorts y LinkedIn.
    No generes imagenes. Genera prompts, conceptos y copies listos para copiar.
  </task>

  <context_json>{json.dumps(payload, ensure_ascii=False, indent=2)}</context_json>

  <rules>
    - Escribe en espanol.
    - Pensamiento Lateral: No te quedes en lo obvio. Busca angulos que conecten con deseos profundos, miedos o aspiraciones de la audiencia.
    - No inventes hechos visuales si `visual_context.status` es `pending_visual_extraction`.
    - Si falta evidencia visual, usa composiciones seguras basadas en marca, texto y concepto, marcando supuestos.
    - Cada prompt debe ser especifico, accionable y util para una herramienta externa.
    - Evita prompts genericos como "imagen limpia y moderna" sin composicion, intencion, copy overlay y razon estrategica.
    - No incluyas secretos ni datos de configuracion.
  </rules>

  <output_schema>
    Devuelve exclusivamente JSON valido:
    {{
      "pack_metadata": {{"brand_name": "texto", "video_id": "texto", "pack_version": "{self.PACK_VERSION}", "generated_for": ["herramienta"], "source_confidence": "fuerte|requiere_revision|basado_en_supuestos"}},
      "strategy": {{"big_idea": "texto", "core_tension": "texto", "audience": "texto", "creative_angle": "texto", "offer_message": "texto"}},
      "channel_packs": [
        {{"channel": "instagram|tiktok|youtube_shorts|youtube_thumbnail|linkedin|meta_ads|stories|carousel", "objective": "texto", "asset_type": "texto", "aspect_ratio": "texto", "hook": "texto", "copy_overlay": "texto", "caption_or_primary_text": "texto", "cta": "texto", "prompt": "texto detallado", "negative_prompt": "texto", "tool_notes": "texto", "why_it_works": "texto", "quality_badge": "fuerte|requiere_revision|basado_en_supuestos"}}
      ],
      "adsets": [
        {{"name": "texto", "objective": "awareness|traffic|leads|sales|retargeting", "audience": "texto", "angle": "texto", "primary_text": "texto", "headline": "texto", "description": "texto", "visual_prompt": "texto", "cta": "texto"}}
      ],
      "message_variants": [
        {{"use": "dm|email|caption|comment_reply|story_reply", "tone": "texto", "message": "texto"}}
      ],
      "external_tool_exports": [
        {{"tool": "Midjourney|Ideogram|Canva|Meta Ads|TikTok/Reels|LinkedIn", "instructions": "texto", "copy_ready_prompt": "texto"}}
      ],
      "production_notes": ["texto"]
    }}
  </output_schema>
</scriptdna_creative_lab>
""".strip()

    def _fallback_pack(self, context: dict, reason: str) -> dict:
        brand = context["brand_name"]
        cta = context["brand_profile"].get("cta") or "Solicitar más información"
        audience = context["brand_profile"].get("audience") or "audiencia interesada en la propuesta"
        tone = context["brand_profile"].get("tone") or "claro, experto y accionable"
        visual_style = context["brand_profile"].get("visual_style") or "limpio, editorial y enfocado"
        excerpt = (context["script_text"] or "").strip()[:240] or "contenido base del video"
        hook = self._first_hook(context) or "La idea que conviene convertir en una pieza visual"
        visual_pending = context["visual_context"].get("status") == "pending_visual_extraction"
        badge = self._quality_badge(context)
        assumption = "Sin evidencia visual verificada; usar composición conceptual basada en marca y guion." if visual_pending else "Usar contexto visual verificado del video."

        channel_packs = []
        for index, (channel, channel_label, aspect_ratio) in enumerate(self.CHANNELS, start=1):
            asset_type = self.ASSET_TYPES[(index - 1) % len(self.ASSET_TYPES)]
            objective = self._objective_for(channel)
            copy_overlay = self._overlay_for(channel, hook)
            prompt = (
                f"{channel_label} para {brand}. Objetivo: {objective}. Audiencia: {audience}. "
                f"Concepto visual: representar la tension entre el problema implicito del guion y la solucion de la marca, "
                f"con estilo {visual_style}, jerarquia clara, espacio seguro para texto, composicion editorial de alto contraste. "
                f"Asset: {asset_type}. Copy overlay: '{copy_overlay}'. CTA: {cta}. "
                f"Referencia textual del video: {excerpt}. {assumption}"
            )
            channel_packs.append({
                "id": f"{channel}-{index:02d}",
                "channel": channel,
                "objective": objective,
                "asset_type": asset_type,
                "aspect_ratio": aspect_ratio,
                "hook": hook,
                "copy_overlay": copy_overlay,
                "caption_or_primary_text": self._caption_for(channel, hook, cta, tone),
                "cta": cta,
                "prompt": prompt,
                "negative_prompt": "texto ilegible, logo deformado, promesas no verificables, exceso de elementos, estética genérica",
                "tool_notes": self._tool_notes_for(channel),
                "why_it_works": "Convierte el guion en una pieza concreta con objetivo, audiencia, composición, copy y CTA listos para producción externa.",
                "quality_badge": badge,
            })

        adsets = [
            {
                "name": f"{brand} - Awareness - Insight principal",
                "objective": "awareness",
                "audience": audience,
                "angle": "autoridad y claridad",
                "primary_text": f"{hook}. {excerpt}",
                "headline": "Convierte esta idea en acción",
                "description": "Pieza pensada para validar interés inicial.",
                "visual_prompt": channel_packs[5]["prompt"],
                "cta": cta,
            },
            {
                "name": f"{brand} - Leads - Problema/Solución",
                "objective": "leads",
                "audience": audience,
                "angle": "problema/solución",
                "primary_text": f"Si esto te está pasando, este es el siguiente paso: {cta}.",
                "headline": "Una solución más clara",
                "description": "Usar como variante directa para pauta.",
                "visual_prompt": channel_packs[4]["prompt"],
                "cta": cta,
            },
        ]

        return {
            "pack_metadata": {
                "brand_name": brand,
                "video_id": context["video_id"],
                "pack_version": self.PACK_VERSION,
                "generated_for": ["Midjourney", "Ideogram", "Canva", "Meta Ads", "TikTok/Reels", "LinkedIn"],
                "source_confidence": badge,
                "generation_note": f"Fallback local: {reason}",
            },
            "strategy": {
                "big_idea": hook,
                "core_tension": "Transformar un contenido puntual en un sistema de piezas reutilizables.",
                "audience": audience,
                "creative_angle": "claridad, autoridad y reutilización inteligente",
                "offer_message": cta,
            },
            "channel_packs": channel_packs,
            "adsets": adsets,
            "message_variants": [
                {"use": "dm", "tone": tone, "message": f"Vi que este tema puede servirte. {hook}. ¿Quieres que te comparta el recurso completo?"},
                {"use": "caption", "tone": tone, "message": f"{hook}\n\n{excerpt}\n\n{cta}"},
                {"use": "story_reply", "tone": tone, "message": f"Si quieres profundizar en esto, responde 'info' y te paso el siguiente paso."},
            ],
            "external_tool_exports": [
                {"tool": "Midjourney", "instructions": "Usar el prompt visual, añadir el aspect ratio indicado y evitar texto pequeño.", "copy_ready_prompt": channel_packs[0]["prompt"]},
                {"tool": "Ideogram", "instructions": "Ideal para composiciones con copy overlay; respetar frase exacta.", "copy_ready_prompt": channel_packs[3]["prompt"]},
                {"tool": "Canva", "instructions": "Crear plantilla con jerarquia: hook, visual central, CTA y marca.", "copy_ready_prompt": channel_packs[7]["prompt"]},
                {"tool": "Meta Ads", "instructions": "Usar adsets y variar headline/primary text por objetivo.", "copy_ready_prompt": adsets[0]["visual_prompt"]},
            ],
            "production_notes": [
                "No se generaron imágenes dentro de ScriptDNA.",
                "Revisar visualmente cada pieza antes de publicarla.",
                assumption,
            ],
        }

    def _normalize_pack(self, pack: dict, context: dict, generation_mode: str, ai_provider: str, ai_model: Optional[str]) -> dict:
        fallback = self._fallback_pack(context, "normalizacion")
        normalized = {
            "pack_metadata": self._as_dict(pack.get("pack_metadata")) or fallback["pack_metadata"],
            "strategy": self._as_dict(pack.get("strategy")) or fallback["strategy"],
            "channel_packs": self._as_list(pack.get("channel_packs")) or fallback["channel_packs"],
            "adsets": self._as_list(pack.get("adsets")) or fallback["adsets"],
            "message_variants": self._as_list(pack.get("message_variants")) or fallback["message_variants"],
            "external_tool_exports": self._as_list(pack.get("external_tool_exports")) or fallback["external_tool_exports"],
            "production_notes": self._as_list(pack.get("production_notes")) or fallback["production_notes"],
        }
        metadata = normalized["pack_metadata"]
        metadata["brand_name"] = context["brand_name"]
        metadata["video_id"] = context["video_id"]
        metadata["pack_version"] = self.PACK_VERSION
        metadata["generated_at"] = datetime.utcnow().isoformat() + "Z"
        metadata["generation_mode"] = generation_mode
        metadata["provider"] = pack.get("_ai_provider", ai_provider) if isinstance(pack, dict) else ai_provider
        metadata["model"] = pack.get("_ai_model", ai_model or (ai_provider_service.default_model_for(ai_provider) if ai_provider != "local" else "deterministic")) if isinstance(pack, dict) else ai_model
        metadata["source_confidence"] = metadata.get("source_confidence") or self._quality_badge(context)
        normalized["pack_metadata"] = metadata

        for index, item in enumerate(normalized["channel_packs"], start=1):
            if isinstance(item, dict):
                item.setdefault("id", f"creative-{index:02d}")
                item.setdefault("quality_badge", metadata["source_confidence"])
        return normalized

    def _write_pack(self, creative_dir: Path, pack: dict) -> None:
        vault_service.save_json(creative_dir, "creative_pack.json", pack)
        vault_service.save_file(creative_dir, "creative_pack.md", self._as_markdown(pack))

    def _as_markdown(self, pack: dict) -> str:
        metadata = pack.get("pack_metadata", {})
        strategy = pack.get("strategy", {})
        lines = [
            f"# Creative Pack - {metadata.get('brand_name')} / {metadata.get('video_id')}",
            "",
            f"- Version: {metadata.get('pack_version')}",
            f"- Generado: {metadata.get('generated_at')}",
            f"- Calidad: {metadata.get('source_confidence')}",
            "",
            "## Estrategia",
            "",
            f"- Big idea: {strategy.get('big_idea', '')}",
            f"- Tensión: {strategy.get('core_tension', '')}",
            f"- Audiencia: {strategy.get('audience', '')}",
            f"- Ángulo: {strategy.get('creative_angle', '')}",
            "",
            "## Prompts por canal",
        ]
        for item in pack.get("channel_packs", []):
            lines.extend([
                "",
                f"### {item.get('channel', 'canal')} - {item.get('asset_type', 'asset')}",
                f"- Objetivo: {item.get('objective', '')}",
                f"- Aspect ratio: {item.get('aspect_ratio', '')}",
                f"- Hook: {item.get('hook', '')}",
                f"- Copy overlay: {item.get('copy_overlay', '')}",
                f"- CTA: {item.get('cta', '')}",
                "",
                "```text",
                item.get("prompt", ""),
                "```",
                "",
                f"Negative prompt: {item.get('negative_prompt', '')}",
                f"Notas: {item.get('tool_notes', '')}",
                f"Por qué funciona: {item.get('why_it_works', '')}",
            ])
        lines.extend(["", "## Adsets"])
        for adset in pack.get("adsets", []):
            lines.extend([
                "",
                f"### {adset.get('name', 'Adset')}",
                f"- Objetivo: {adset.get('objective', '')}",
                f"- Audiencia: {adset.get('audience', '')}",
                f"- Ángulo: {adset.get('angle', '')}",
                f"- Headline: {adset.get('headline', '')}",
                f"- Texto principal: {adset.get('primary_text', '')}",
                f"- CTA: {adset.get('cta', '')}",
            ])
        return "\n".join(lines).strip() + "\n"

    def _quality_badge(self, context: dict) -> str:
        audit = context.get("audit") or {}
        score = audit.get("overall_score")
        warnings = audit.get("warnings") or []
        visual_status = (context.get("visual_context") or {}).get("status")
        if visual_status == "pending_visual_extraction" or any("supuesto" in str(item).lower() for item in warnings):
            return "basado_en_supuestos"
        if isinstance(score, (int, float)) and score >= 8:
            return "fuerte"
        return "requiere_revision"

    def _first_hook(self, context: dict) -> Optional[str]:
        hooks = context.get("hooks") or []
        for item in hooks:
            if isinstance(item, dict) and item.get("hook"):
                return item["hook"]
        ads = context.get("ads") or []
        for item in ads:
            if isinstance(item, dict) and (item.get("angulo") or item.get("concepto")):
                return item.get("angulo") or item.get("concepto")
        return None

    def _objective_for(self, channel: str) -> str:
        return {
            "instagram": "guardar y compartir",
            "tiktok": "retención rápida y comentario",
            "youtube_shorts": "retención y suscripción",
            "youtube_thumbnail": "clic inicial",
            "linkedin": "autoridad y conversación profesional",
            "meta_ads": "validación de ángulo para pauta",
            "stories": "respuesta directa",
            "carousel": "educación y guardados",
        }.get(channel, "activar interés")

    def _overlay_for(self, channel: str, hook: str) -> str:
        short = hook[:58].rstrip()
        if channel == "youtube_thumbnail":
            return short or "La idea clave"
        if channel in {"stories", "tiktok", "youtube_shorts"}:
            return short or "Mira esto antes de decidir"
        return short or "Una forma más clara de verlo"

    def _caption_for(self, channel: str, hook: str, cta: str, tone: str) -> str:
        if channel == "linkedin":
            return f"{hook}\n\nUna lectura práctica para equipos que necesitan convertir contenido en decisiones.\n\n{cta}"
        if channel == "meta_ads":
            return f"{hook}. Descubre el siguiente paso y actúa con más claridad. {cta}"
        return f"{hook}\n\n{cta}"

    def _tool_notes_for(self, channel: str) -> str:
        if channel == "youtube_thumbnail":
            return "Optimizar en Ideogram o Canva con texto grande y contraste alto."
        if channel == "meta_ads":
            return "Usar en Meta Ads como visual principal y testear 2-3 copies."
        if channel in {"tiktok", "youtube_shorts", "stories"}:
            return "Pensado para formato vertical; mantener copy breve en zona segura."
        return "Usar en Midjourney, Ideogram o Canva y adaptar tipografía de marca."

    def _as_dict(self, value) -> dict:
        return value if isinstance(value, dict) else {}

    def _as_list(self, value) -> list:
        return value if isinstance(value, list) else []


creative_pack_service = CreativePackService()
