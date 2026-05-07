import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from statistics import mean

try:
    from services.ai_provider_service import ai_provider_service
except ModuleNotFoundError:
    from backend.services.ai_provider_service import ai_provider_service

class CreativeAuditService:
    AUDIT_VERSION = "scriptdna-creative-audit-v1"

    def audit_pack(self, pack: dict, strategic_analysis: dict) -> dict:
        """
        Realiza una auditoría de coherencia sobre el Creative Pack generado.
        """
        metadata = pack.get("pack_metadata", {})
        strategy = pack.get("strategy", {})
        channels = pack.get("channel_packs", [])
        
        # 1. Definir criterios de evaluación
        scores = {
            "coherencia_estrategica": self._score_strategic_coherence(strategy, strategic_analysis),
            "alineacion_visual": self._score_visual_alignment(channels, strategy, strategic_analysis),
            "consistencia_mensaje": self._score_message_consistency(channels, strategy),
            "adaptacion_canal": self._score_channel_adaptation(channels),
            "calidad_prompts": self._score_prompt_quality(channels),
        }
        
        overall = round(mean(scores.values()), 2)
        
        # 2. Generar recomendaciones
        recommendations = self._generate_recommendations(scores, channels)
        
        audit = {
            "audit_version": self.AUDIT_VERSION,
            "status": "passed" if overall >= 7.5 else "needs_refinement",
            "overall_score": overall,
            "scores": scores,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "brand_name": metadata.get("brand_name"),
                "video_id": metadata.get("video_id"),
                "pack_version": metadata.get("pack_version"),
            }
        }
        
        return audit

    def _score_strategic_coherence(self, strategy: dict, analysis: dict) -> float:
        """Mide qué tan bien la Big Idea del pack refleja el insight lateral del análisis."""
        big_idea = strategy.get("big_idea", "").lower()
        lateral_insight = analysis.get("retrospectiva", {}).get("insight_lateral", "").lower()
        
        if not big_idea or not lateral_insight:
            return 5.0
            
        # Simulación de cruce de keywords (en producción esto podría ser un prompt de IA)
        keywords = ["insight", "tension", "deseo", "miedo", "oportunidad"]
        hits = sum(1 for k in keywords if k in big_idea and k in lateral_insight)
        
        return round(min(10, 6 + hits * 1.5), 2)

    def _score_visual_alignment(self, channels: List[dict], strategy: dict, analysis: dict) -> float:
        """Verifica que los prompts visuales sigan el Estética DNA y la Big Idea."""
        prompts = [c.get("prompt", "").lower() for c in channels]
        visual_style = analysis.get("brief_creativo", "").lower() # O del perfil de marca
        
        if not prompts:
            return 0.0
            
        # Buscar palabras clave de la estética en los prompts
        score = 5.0
        if any("composition" in p or "lighting" in p for p in prompts):
            score += 2.0
        if any(strategy.get("big_idea", "").lower()[:20] in p for p in prompts):
            score += 2.0
            
        return round(min(10, score), 2)

    def _score_message_consistency(self, channels: List[dict], strategy: dict) -> float:
        """Asegura que el mensaje central no se diluya entre canales."""
        hooks = [c.get("hook", "").lower() for c in channels]
        main_hook = strategy.get("big_idea", "").lower()
        
        if not hooks:
            return 0.0
            
        consistency = sum(1 for h in hooks if any(word in h for word in main_hook.split()[:5]))
        return round(min(10, 4 + (consistency / len(hooks)) * 6), 2)

    def _score_channel_adaptation(self, channels: List[dict]) -> float:
        """Evalúa si los formatos y CTAs son correctos para cada red social."""
        score = 10.0
        for c in channels:
            channel = c.get("channel", "")
            ratio = c.get("aspect_ratio", "")
            if channel in ["instagram", "tiktok", "stories"] and "9:16" not in ratio:
                score -= 1.0
            if channel == "youtube_thumbnail" and "16:9" not in ratio:
                score -= 1.0
        return round(max(0, score), 2)

    def _score_prompt_quality(self, channels: List[dict]) -> float:
        """Mide la riqueza técnica de los prompts para herramientas externas."""
        prompts = [c.get("prompt", "") for c in channels]
        if not prompts:
            return 0.0
            
        avg_words = mean(len(p.split()) for p in prompts)
        # Un prompt de menos de 15 palabras suele ser genérico
        return round(min(10, avg_words / 4), 2)

    def _generate_recommendations(self, scores: dict, channels: List[dict]) -> List[str]:
        recs = []
        if scores["coherencia_estrategica"] < 7:
            recs.append("La Big Idea es demasiado genérica; reconectar con el Insight Lateral del análisis.")
        if scores["calidad_prompts"] < 7:
            recs.append("Los prompts visuales carecen de detalles técnicos (iluminación, composición, estilo de cámara).")
        if scores["consistencia_mensaje"] < 7:
            recs.append("El mensaje varía demasiado entre canales. Unificar el gancho narrativo.")
        return recs

creative_audit_service = CreativeAuditService()
