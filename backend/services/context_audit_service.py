import json
import re
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any, Optional

try:
    from services.vault_service import vault_service
    from services.training_service import training_service
except ModuleNotFoundError:
    from backend.services.vault_service import vault_service
    from backend.services.training_service import training_service


class ContextAuditService:
    AUDIT_VERSION = "scriptdna-context-audit-v1"
    REQUIRED_KEYS = [
        "resumen_ejecutivo",
        "hooks",
        "momentos_virales",
        "estructura_narrativa",
        "ideas_reels",
        "ads",
        "brief_creativo",
        "captions",
        "calendario_publicacion",
        "prompts_visuales",
        "prompt_base_marca",
        "retrospectiva",
    ]
    STOPWORDS = {
        "para", "como", "esta", "este", "esto", "pero", "porque", "desde", "sobre", "entre",
        "tambien", "donde", "cuando", "video", "marca", "contenido", "guion", "texto", "todo",
        "una", "uno", "unos", "unas", "los", "las", "del", "con", "por", "que", "hay",
        "este", "esta", "estos", "estas", "como", "pero", "para", "todo", "todos", "todas"
    }
    
    COMMON_SPANISH_TITLES = {
        "Hola", "Bienvenidos", "Gracias", "Entonces", "Además", "Finalmente", "Primero",
        "Segundo", "Tercero", "Luego", "Después", "Porque", "Cuando", "Donde", "Desde",
        "Sobre", "Entre", "Hacia", "Para", "Pero", "Como", "Si", "No", "Sí", "Este", "Esta",
        "Análisis", "Estratégico", "Arbitraje", "Necesidad", "Latente", "Tema", "Insight", "Lateral",
        "Objetivo", "Tono", "Oportunidad", "Negocio", "Hook", "Gancho", "Uso", "Rationale",
        "Título", "Descripción", "Motivo", "Retención", "Patrón", "Notas", "Estructura",
        "Concepto", "Ángulo", "Copy", "Brief", "Creativo", "Mensaje", "Central", "Dirección",
        "Visual", "Plataforma", "Caption", "Hashtags", "Día", "Pieza", "Prompt", "Base",
        "Marca", "Retrospectiva", "Siguiente", "Mejora", "Mientras", "Daniel", "Real", "Estate",
        "Trámites", "Migratorios", "Seguros", "Masterclass", "Haz", "Clic", "Inversión", "Retorno",
        "Eficacia", "Probada", "Operativo", "Infraestructura", "Instagram", "TikTok", "LinkedIn",
        "YouTube", "Shorts", "Meta", "Ads", "Duelo", "Industrias", "Revelación", "Escalabilidad",
        "Acelerada", "Sector", "Aburrido", "Aceptarías", "Alta", "Apela", "Aprende", "Captación",
        "Carrusel", "Comenta", "Conecta", "Convertir", "Corte", "Deja", "Demo", "Deseo",
        "Desmitifica", "Detalles", "Dueños", "Educación", "Emprendimiento", "Enfatizar",
        "Engagement", "Eres", "Factura", "Facturación", "Growth", "Hablemos", "Identifica",
        "Ignorar", "Integrar", "Inteligente", "Interfaz", "Justificación", "Llamado",
        "Mecanismo", "Mencionar", "Mira", "Posicionarse", "Prometer", "Prueba", "Referencia",
        "Referenciar", "Registrarme", "Reservar", "Selección", "Tienes", "Usar", "Validar",
        "Vende", "Video", "Aprovecha", "Busca", "Crea", "Descubre", "Encuentra", "Genera",
        "Habla", "Inicia", "Junta", "Logra", "Mejora", "Mira", "Nosotros", "Obtén", "Presenta",
        "Qué", "Recuerda", "Sé", "Ten", "Usa", "Vive", "Ya", "Comparativo", "Texto", "Dominio",
        "Posicionar", "Convierte", "Capturar", "Thirds", "Introduce", "Presentar", "Contrastar",
        "Winner", "Reto", "Pasa", "Medir", "Abre", "Abrir", "Demanda", "Lower", "Story",
        "Thumbnail", "Portada", "Mueve", "Urgencia", "Business", "True", "Educar", "Adset",
        "Pantalla", "Escena", "Audio", "Corte", "Entrada", "Salida", "Fondo", "Iluminación",
        "Color", "Persona", "Gesto", "Mirada", "Manos", "Voz", "Ritmo", "Música", "Efecto",
        "Transición", "Zoom", "Plano", "Angulo", "Perspectiva", "Enfoque", "Nitidez", "Brillo",
        "Contraste", "Saturación", "Tono", "Vibración", "Energía", "Calma", "Confianza",
        "Autoridad", "Experto", "Líder", "Guía", "Acompañamiento", "Solución", "Resultado"
    }

    def audit_all(self) -> dict:
        audits = []
        for brand in vault_service.list_brands():
            for video in vault_service.list_videos(brand["brand_name"]):
                audit = self.audit_video(video["brand_name"], video["video_id"], save=True)
                if audit:
                    audits.append(audit)
        return self._write_aggregate(audits)

    def latest_report(self) -> dict:
        report_path = self._aggregate_path()
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return self.audit_all()

    def audit_video(self, brand_name: str, video_id: str, save: bool = True) -> Optional[dict]:
        video_path = vault_service.get_video_path(brand_name, video_id)
        analysis_dir = video_path / "Analisis"
        full_analysis = vault_service.read_json(analysis_dir / "full_analysis.json")
        if not full_analysis:
            return None

        script_text = vault_service.read_file(video_path / "guion_original.txt") or ""
        brand_profile = vault_service.get_brand_profile(brand_name)
        visual_context = vault_service.read_json(analysis_dir / "analisis_visual.json") or {}

        scores = {
            "fidelidad": self._score_fidelity(script_text, full_analysis),
            "alineacion_marca": self._score_brand_alignment(brand_profile, full_analysis),
            "especificidad": self._score_specificity(full_analysis),
            "pensamiento_lateral": self._score_lateral_thinking(full_analysis),
            "uso_contexto_visual": self._score_visual_context(visual_context, full_analysis),
            "completitud_json": self._score_completeness(full_analysis),
            "utilidad_marketing": self._score_marketing_usefulness(full_analysis),
            "alucinacion": self._score_hallucination(script_text, brand_profile, visual_context, full_analysis),
            "densidad_info": self._score_density(full_analysis),
            "cumplimiento_marca": self._score_compliance(brand_profile, full_analysis),
            "estructura_persuasiva": self._score_persuasive_structure(full_analysis),
            "quiet_luxury_score": self._score_quiet_luxury(full_analysis),
            "engagement_emocional": self._score_engagement(full_analysis),
            "veracidad": self._score_truthfulness(script_text, full_analysis),
            "estetica_visual": self._score_visual_aesthetic(visual_context),
            "coherencia_visual_narrativa": self._score_visual_narrative_coherence(visual_context, full_analysis),
        }
        overall = round(mean(scores.values()), 2)
        warnings = self._warnings(scores, script_text, visual_context, full_analysis)
        promoted_patterns = self._promote_patterns(brand_name, video_id, full_analysis, overall, scores)
        audit = {
            "audit_version": self.AUDIT_VERSION,
            "status": "passed" if overall >= 7 else "needs_review",
            "brand_name": brand_name,
            "video_id": video_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "overall_score": overall,
            "scores": scores,
            "warnings": warnings,
            "promoted_patterns": promoted_patterns,
            "refinement_instructions": self.generate_refinement_instructions(scores, warnings) if overall < 7.5 else None,
            "context": {
                "script_chars": len(script_text),
                "visual_context_status": visual_context.get("status") or ("available" if visual_context else "missing"),
                "prompt_version": full_analysis.get("_prompt_version"),
                "provider": full_analysis.get("_ai_provider"),
                "model": full_analysis.get("_ai_model"),
            },
        }
        
        if overall < 6:
            for warning in warnings:
                training_service.record_negative_pattern(brand_name, warning, "Bajo puntaje en auditoría", source_video_id=video_id)
        
        training_service.record_skill_evolution(brand_name, overall, warnings)
        
        if save:
            vault_service.save_json(analysis_dir, "auditoria_contexto.json", audit)
        return audit

    def _write_aggregate(self, audits: list[dict]) -> dict:
        report = {
            "audit_version": self.AUDIT_VERSION,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_videos": len(audits),
            "average_score": round(mean([item["overall_score"] for item in audits]), 2) if audits else 0,
            "audits": audits,
        }
        report_path = self._aggregate_path()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
        return report

    def _aggregate_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / "scratch" / "final_qa_audit_report.json"

    def _score_completeness(self, analysis: dict) -> float:
        present = 0
        for key in self.REQUIRED_KEYS:
            value = analysis.get(key)
            if value not in (None, "", [], {}):
                present += 1
        return round((present / len(self.REQUIRED_KEYS)) * 10, 2)

    def _score_fidelity(self, script_text: str, analysis: dict) -> float:
        script_terms = self._keywords(script_text, limit=40)
        if not script_terms:
            return 5.0
        analysis_text = self._flatten_text(analysis).lower()
        hits = sum(1 for term in script_terms if term in analysis_text)
        return round(min(10, 3 + (hits / max(1, len(script_terms))) * 10), 2)

    def _score_brand_alignment(self, brand_profile: dict, analysis: dict) -> float:
        brand_terms = self._keywords(json.dumps(brand_profile, ensure_ascii=False), limit=30)
        if not brand_terms:
            return 6.0
        analysis_text = self._flatten_text(analysis).lower()
        hits = sum(1 for term in brand_terms if term in analysis_text)
        score = 4 + (hits / max(1, len(brand_terms))) * 8
        prompt_base = analysis.get("prompt_base_marca")
        if isinstance(prompt_base, dict) and prompt_base.get("brand_name"):
            score += 1
        return round(min(10, score), 2)

    def _score_specificity(self, analysis: dict) -> float:
        hooks = analysis.get("hooks") if isinstance(analysis.get("hooks"), list) else []
        prompts = analysis.get("prompts_visuales") if isinstance(analysis.get("prompts_visuales"), list) else []
        ads = analysis.get("ads") if isinstance(analysis.get("ads"), list) else []
        lengths = []
        for item in hooks + prompts + ads:
            if isinstance(item, dict):
                lengths.extend(len(str(value).split()) for value in item.values() if isinstance(value, str))
        if not lengths:
            return 4.0
        avg_length = mean(lengths)
        generic_penalty = self._generic_penalty(self._flatten_text({"hooks": hooks, "prompts": prompts, "ads": ads}))
        return round(max(0, min(10, 4 + avg_length / 4 - generic_penalty)), 2)

    def _score_lateral_thinking(self, analysis: dict) -> float:
        text = self._flatten_text(analysis).lower()
        markers = [
            "insight", "lateral", "psicolog", "tension", "simbolo", "cultural", "no obvia",
            "retencion", "deseo", "miedo", "creencia", "contraste", "oportunidad",
        ]
        hits = sum(1 for marker in markers if marker in text)
        return round(min(10, 4 + hits * 0.9), 2)

    def _score_visual_context(self, visual_context: dict, analysis: dict) -> float:
        status = visual_context.get("status") if isinstance(visual_context, dict) else None
        text = self._flatten_text(analysis).lower()
        if not visual_context or status == "pending_visual_extraction":
            unsupported_visuals = any(term in text for term in ["escena", "iluminacion", "colores", "persona", "camara"])
            return 8.0 if not unsupported_visuals else 5.0
        visual_terms = self._keywords(json.dumps(visual_context, ensure_ascii=False), limit=30)
        if not visual_terms:
            return 6.0
        hits = sum(1 for term in visual_terms if term in text)
        return round(min(10, 4 + (hits / max(1, len(visual_terms))) * 10), 2)

    def _score_marketing_usefulness(self, analysis: dict) -> float:
        useful_keys = ["hooks", "ideas_reels", "ads", "captions", "calendario_publicacion", "brief_creativo"]
        score = 2.0
        for key in useful_keys:
            value = analysis.get(key)
            if value not in (None, "", [], {}):
                score += 1.1
        text = self._flatten_text(analysis).lower()
        if "cta" in text:
            score += 1
        if any(term in text for term in ["objetivo", "audiencia", "plataforma", "pieza"]):
            score += 0.8
        return round(min(10, score), 2)

    def _warnings(self, scores: dict, script_text: str, visual_context: dict, analysis: dict) -> list[str]:
        warnings = []
        for key, score in scores.items():
            if score < 6:
                warnings.append(f"{key} bajo ({score}/10).")
        if len(script_text.strip()) < 200:
            warnings.append("Guion corto: revisar supuestos antes de usar outputs en producción.")
        if visual_context.get("status") == "pending_visual_extraction" and scores["uso_contexto_visual"] < 7:
            warnings.append("Contexto visual pendiente: evitar asumir estética o escenas verificadas.")
        if self._generic_penalty(self._flatten_text(analysis)) >= 2:
            warnings.append("Se detectan frases genéricas; conviene exigir más evidencia y especificidad.")
        
        if scores.get("cumplimiento_marca", 10) < 10:
            warnings.append("USO DE PALABRAS PROHIBIDAS: Revisa el perfil de marca y elimina términos no permitidos.")
        if scores.get("quiet_luxury_score", 10) < 6:
            warnings.append("Tono demasiado agresivo (Loud Marketing): Se recomienda suavizar el lenguaje hacia el 'Quiet Luxury'.")
        if scores.get("estructura_persuasiva", 10) < 7:
            warnings.append("Estructura débil: Falta un Hook claro o un CTA directo en algunos módulos.")
        if scores.get("engagement_emocional", 10) < 6:
            warnings.append("Falta de resonancia emocional: El contenido se siente plano o puramente informativo.")
            
        return warnings

    def _promote_patterns(self, brand_name: str, video_id: str, analysis: dict, overall_score: float, scores: dict) -> bool:
        core_scores = [
            scores.get("fidelidad", 0),
            scores.get("especificidad", 0),
            scores.get("pensamiento_lateral", 0),
        ]
        if overall_score < 7 or any(score < 6 for score in core_scores):
            return False
        hooks = [item.get("hook") for item in analysis.get("hooks", []) if isinstance(item, dict)]
        structures = analysis.get("estructura_narrativa", {}).get("patron", []) if isinstance(analysis.get("estructura_narrativa"), dict) else []
        angles = [item.get("angulo") or item.get("concepto") for item in analysis.get("ads", []) if isinstance(item, dict)]
        style_rules = analysis.get("prompt_base_marca", {}).get("do", []) if isinstance(analysis.get("prompt_base_marca"), dict) else []
        vault_service.update_brand_patterns(
            brand_name,
            {
                "hooks_frecuentes": hooks[:8],
                "estructuras_ganadoras": structures if isinstance(structures, list) else [structures],
                "angulos_de_venta": angles[:8],
                "reglas_de_estilo": style_rules[:8],
            },
            source_video_id=video_id,
            prompt_version=analysis.get("_prompt_version"),
            audit_score=overall_score,
            promote=True,
        )
        return True

    def _keywords(self, text: str, limit: int = 30) -> list[str]:
        words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]{4,}", (text or "").lower())
        seen = []
        for word in words:
            if word in self.STOPWORDS or word in seen:
                continue
            seen.append(word)
            if len(seen) >= limit:
                break
        return seen

    def _flatten_text(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._flatten_text(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._flatten_text(item) for item in value)
        return str(value or "")

    def _generic_penalty(self, text: str) -> float:
        generic_markers = [
            "alta calidad", "impacta en el mercado", "impulsar tu negocio",
            "conocer mas", "contenido de valor", "idea principal",
            "mejorar resultados", "estrategia ganadora", "potencial ilimitado"
        ]
        lowered = text.lower()
        return sum(1 for marker in generic_markers if marker in lowered) * 0.8

    def _score_hallucination(self, script_text: str, brand_profile: dict, visual_context: dict, analysis: dict) -> float:
        """Detecta si el modelo inventó nombres, hechos o marcas no presentes en el contexto."""
        all_context = script_text + json.dumps(brand_profile) + json.dumps(visual_context)
        context_keywords = set(self._keywords(all_context, limit=200))
        
        # Extraer palabras capitalizadas que podrían ser nombres propios
        analysis_text = self._flatten_text(analysis)
        # Buscar palabras que empiezan con mayúscula y NO son el inicio de una frase (aprox)
        # O simplemente filtrar palabras comunes que suelen ir al inicio
        proper_nouns = set(re.findall(r"\b[A-Z][a-z]{3,}\b", analysis_text))
        
        hallucination_penalty = 0
        for noun in proper_nouns:
            if noun in self.COMMON_SPANISH_TITLES:
                continue
            if noun.lower() in context_keywords or noun in all_context:
                continue
            
            # Penalización reducida por palabra sospechosa para evitar castigos excesivos por falsos positivos
            hallucination_penalty += 0.8
                
        return round(max(0, 10 - hallucination_penalty), 2)

    def _score_density(self, analysis: dict) -> float:
        """Mide la riqueza informativa del JSON generado."""
        total_words = len(self._flatten_text(analysis).split())
        num_keys = len(analysis.keys())
        density = total_words / max(1, num_keys)
        
        # Idealmente queremos entre 15 y 40 palabras por módulo
        if 15 <= density <= 45:
            return 10.0
        if density < 15:
            return round(density / 1.5, 2)
        return 8.0 # Demasiada verbosidad también puede ser negativa

    def _score_compliance(self, brand_profile: dict, analysis: dict) -> float:
        """Verifica que no se usen palabras prohibidas y se sigan restricciones críticas."""
        forbidden = brand_profile.get("forbidden_words", [])
        if not forbidden:
            return 10.0
        
        text = self._flatten_text(analysis).lower()
        penalties = 0
        for word in forbidden:
            if word.lower() in text:
                penalties += 2.0
                
        return round(max(0, 10 - penalties), 2)

    def _score_persuasive_structure(self, analysis: dict) -> float:
        """Evalúa si el contenido sigue una progresión lógica de ventas/marketing."""
        text = self._flatten_text(analysis).lower()
        # Buscamos elementos de una estructura AIDA o similar
        has_hook = any(h in text for h in ["hook", "gancho", "atencion"])
        has_tension = any(t in text for t in ["tension", "problema", "deseo", "miedo"])
        has_solution = any(s in text for s in ["solucion", "oferta", "beneficio"])
        has_cta = any(c in text for c in ["cta", "llamado a la accion", "click", "comprar"])
        
        score = 2.0
        if has_hook: score += 2
        if has_tension: score += 2
        if has_solution: score += 2
        if has_cta: score += 2
        
        return round(min(10, score), 2)

    def _score_quiet_luxury(self, analysis: dict) -> float:
        """Mide la elegancia y sutileza del lenguaje (evitando 'loud marketing')."""
        text = self._flatten_text(analysis).lower()
        # Palabras "Loud" que restan puntos a Quiet Luxury
        loud_markers = ["barato", "oferton", "increible", "urgente", "compra ya", "garantizado", "el mejor", "unico"]
        # Palabras "Quiet" que suman puntos
        quiet_markers = ["artesanal", "curad", "atemporal", "esencial", "sutil", "experiencia", "detalle", "legado"]
        
        loud_count = sum(1 for m in loud_markers if m in text)
        quiet_count = sum(1 for m in quiet_markers if m in text)
        
        score = 7.0 - (loud_count * 1.5) + (quiet_count * 0.8)
        return round(max(0, min(10, score)), 2)

    def _score_engagement(self, analysis: dict) -> float:
        """Evalúa el potencial de resonancia emocional y engagement."""
        text = self._flatten_text(analysis).lower()
        # Gatillos emocionales y sociales
        triggers = [
            "curiosidad", "secreto", "miedo", "deseo", "prueba social", "autoridad",
            "exclusivo", "pertenencia", "historia", "transformacion", "antes", "despues"
        ]
        hits = sum(1 for t in triggers if t in text)
        
        # También buscamos elementos que fomenten interacción
        interaction = ["pregunta", "comenta", "comparte", "guarda", "etiqueta"]
        int_hits = sum(1 for i in interaction if i in text)
        
        score = 3.0 + (hits * 0.8) + (int_hits * 1.0)
        return round(min(10, score), 2)

    def _score_truthfulness(self, script_text: str, analysis: dict) -> float:
        """Verifica que las promesas y hooks estén respaldados por el guion."""
        hooks = [item.get("hook", "") for item in analysis.get("hooks", []) if isinstance(item, dict)]
        ads = [item.get("angulo", "") for item in analysis.get("ads", []) if isinstance(item, dict)]
        claims = hooks + ads
        
        if not claims:
            return 10.0
            
        script_words = set(self._keywords(script_text, limit=300))
        unsupported_count = 0
        
        for claim in claims:
            claim_words = self._keywords(claim, limit=10)
            # Si ninguna palabra clave del claim está en el guion (y no son genéricas)
            if not any(word in script_words for word in claim_words):
                unsupported_count += 1
                
        # Cada claim no respaldado resta 1.5 puntos
        return round(max(0, 10 - unsupported_count * 1.5), 2)

    def _score_visual_aesthetic(self, visual_context: dict) -> float:
        """Evalúa el ADN estético del video (Quiet Luxury vs Loud Marketing)."""
        dna = visual_context.get("estetica_dna")
        if not dna or not isinstance(dna, dict):
            return 7.0 # Neutral si no hay datos
            
        vibe = dna.get("vibe", "neutral")
        iluminacion = dna.get("iluminacion", "")
        estabilidad = dna.get("estabilidad", "")
        
        score = 6.0
        
        # Premiar Quiet Luxury
        if vibe == "quiet_luxury": score += 2.5
        elif vibe == "loud_marketing": score -= 2.0
        
        # Premiar calidad técnica
        if "suave" in iluminacion or "natural" in iluminacion: score += 1.0
        if estabilidad == "alta": score += 0.5
        
        return round(max(0, min(10, score)), 2)

    def _score_visual_narrative_coherence(self, visual_context: dict, analysis: dict) -> float:
        """Verifica si el output menciona elementos del escenario o visuales reales del video."""
        status = visual_context.get("status")
        if not visual_context or status in ("pending_visual_extraction", "no_frames_found", "error"):
            return 8.0 # No podemos validar, asumimos neutralidad positiva
            
        # Extraer palabras clave del contexto visual (escenario, elementos, estilo)
        visual_text = f"{visual_context.get('escenario', '')} {' '.join(visual_context.get('elementos_clave', []))} {visual_context.get('estilo_visual', '')}"
        visual_elements = set(self._keywords(visual_text, limit=40))
        
        if not visual_elements:
             return 7.0
             
        analysis_text = self._flatten_text(analysis).lower()
        # Buscamos coincidencias de elementos visuales en el análisis
        hits = sum(1 for element in visual_elements if element in analysis_text)
        
        # El score depende de cuántas señales visuales se integraron en el copy/estrategia
        score = 5.0 + (hits * 1.5)
        return round(min(10, score), 2)

    def generate_refinement_instructions(self, scores: dict, warnings: list[str]) -> str:
        """Convierte los resultados de la auditoría en instrucciones de mejora."""
        instructions = ["AUDITORIA DETECTÓ DEFICIENCIAS. REFINA EL OUTPUT SIGUIENDO ESTO:"]
        
        if scores.get("fidelidad", 10) < 7:
            instructions.append("- Apegarse estrictamente al guion original. No inventar diálogos.")
        if scores.get("especificidad", 10) < 7:
            instructions.append("- Evitar frases genéricas. Usar datos concretos y ejemplos precisos.")
        if scores.get("pensamiento_lateral", 10) < 7:
            instructions.append("- Profundizar en el 'insight lateral'. Ir más allá de lo obvio.")
        if scores.get("alucinacion", 10) < 8:
            instructions.append("- ELIMINAR nombres, marcas o hechos que no estén en el input proporcionado.")
            
        for warning in warnings:
            instructions.append(f"- CORREGIR: {warning}")
            
        return "\n".join(instructions)


context_audit_service = ContextAuditService()
