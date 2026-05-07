import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

try:
    from services.vault_service import vault_service
except ModuleNotFoundError:
    from backend.services.vault_service import vault_service

class TrainingService:
    def __init__(self):
        self.ANTI_PATTERNS_FILENAME = "anti_patrones.json"
        self.SKILL_EVOLUTION_FILENAME = "evolucion_skills.json"

    def record_negative_pattern(self, brand_name: str, pattern: str, reason: str, source_video_id: Optional[str] = None):
        """Registra un patrón que no funcionó para evitarlo en el futuro."""
        brand_path = vault_service.create_brand_structure(brand_name)
        file_path = brand_path / "Analisis" / self.ANTI_PATTERNS_FILENAME
        
        data = vault_service.read_json(file_path) or {"anti_patterns": []}
        
        # Evitar duplicados
        if any(item["pattern"].lower() == pattern.lower() for item in data["anti_patterns"]):
            return data
            
        data["anti_patterns"].append({
            "pattern": pattern,
            "reason": reason,
            "source_video_id": source_video_id,
            "recorded_at": datetime.utcnow().isoformat() + "Z"
        })
        
        # Mantener solo los últimos 50 anti-patrones para no saturar el contexto
        data["anti_patterns"] = data["anti_patterns"][-50:]
        
        vault_service.save_json(brand_path / "Analisis", self.ANTI_PATTERNS_FILENAME, data)
        return data

    def get_negative_memory(self, brand_name: str) -> List[dict]:
        """Obtiene la memoria de lo que NO se debe hacer."""
        brand_path = vault_service.create_brand_structure(brand_name)
        file_path = brand_path / "Analisis" / self.ANTI_PATTERNS_FILENAME
        data = vault_service.read_json(file_path) or {"anti_patterns": []}
        return data["anti_patterns"]

    def record_skill_evolution(self, brand_name: str, audit_score: float, improvements: List[str]):
        """Registra cómo está evolucionando la calidad de los outputs."""
        brand_path = vault_service.create_brand_structure(brand_name)
        file_path = brand_path / "Analisis" / self.SKILL_EVOLUTION_FILENAME
        
        data = vault_service.read_json(file_path) or {"history": [], "current_level": "novice"}
        
        data["history"].append({
            "score": audit_score,
            "improvements": improvements,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # Lógica simple de nivel
        avg_score = sum(h["score"] for h in data["history"][-5:]) / min(len(data["history"]), 5)
        if avg_score > 8.5:
            data["current_level"] = "expert"
        elif avg_score > 7:
            data["current_level"] = "intermediate"
        else:
            data["current_level"] = "novice"
            
        vault_service.save_json(brand_path / "Analisis", self.SKILL_EVOLUTION_FILENAME, data)
        return data

    def consolidate_brand_intelligence(self, brand_name: str, ai_provider: str = "gemini"):
        """Analiza la historia reciente para extraer reglas de estilo definitivas."""
        brand_path = vault_service.create_brand_structure(brand_name)
        history_path = brand_path / "Analisis" / self.SKILL_EVOLUTION_FILENAME
        history_data = vault_service.read_json(history_path) or {"history": []}
        
        recent = history_data["history"][-10:]
        if not recent:
            return None
            
        # Preparar contexto para la consolidación
        context = []
        for h in recent:
            status = "EXITO" if h["score"] > 8 else "MEJORABLE"
            context.append(f"- Score: {h['score']} ({status}). Notas: {', '.join(h['improvements'])}")
            
        prompt = f"""
        Actúa como el Director Creativo de {brand_name}.
        Hemos analizado los últimos 10 videos y estos son los resultados de auditoría:
        {json.dumps(context, indent=2)}
        
        Tu tarea es extraer:
        1. REGLAS DE ORO: Qué está funcionando (basado en scores altos).
        2. BARRERAS: Qué errores son recurrentes (basado en mejoras sugeridas).
        
        Responde en JSON con esta estructura:
        {{
            "reglas_oro": ["regla"],
            "barreras_criticas": ["evitar esto"],
            "personalidad_detectada": "una frase que resuma el tono actual",
            "proximo_paso_entrenamiento": "una instruccion para la IA"
        }}
        """
        
        try:
            from services.ai_provider_service import ai_provider_service
        except ModuleNotFoundError:
            from backend.services.ai_provider_service import ai_provider_service
            
        try:
            intelligence = ai_provider_service.generate_json(prompt, provider=ai_provider)
        except Exception:
            intelligence = self._fallback_brand_wisdom(brand_name, recent)
        
        # Guardar como sabiduría de marca
        vault_service.save_json(brand_path / "Analisis", "sabiduria_marca.json", intelligence)
        return intelligence

    def _fallback_brand_wisdom(self, brand_name: str, recent: List[dict]) -> dict:
        """Consolida reglas basicas cuando el proveedor IA no esta disponible."""
        improvements = []
        scores = []
        for item in recent:
            scores.append(float(item.get("score", 0) or 0))
            improvements.extend(item.get("improvements", []) or [])

        repeated = []
        for improvement in improvements:
            if improvement and improvement not in repeated:
                repeated.append(improvement)

        average = round(sum(scores) / len(scores), 2) if scores else 0
        return {
            "reglas_oro": [
                f"Mantener el analisis alineado a la marca {brand_name}.",
                "Priorizar ideas accionables que puedan convertirse en contenido, anuncios o prompts.",
                "Validar fidelidad al guion antes de promover patrones de marca.",
            ],
            "barreras_criticas": repeated[:5] or [
                "Evitar conclusiones genericas sin soporte del guion.",
                "Marcar supuestos cuando falte contexto visual o textual.",
            ],
            "personalidad_detectada": f"Marca en aprendizaje con promedio de auditoria {average}/10.",
            "proximo_paso_entrenamiento": "Procesar mas videos y revisar auditorias para consolidar patrones con mayor confianza.",
            "generation_mode": "local_fallback",
        }

training_service = TrainingService()
