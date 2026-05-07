import sys
import os
from pathlib import Path
import json

# Añadir el path del backend
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.ai_provider_service import ai_provider_service

class QAJudge:
    def evaluate_analysis(self, script: str, analysis: dict, brand_profile: dict) -> dict:
        """
        Evalúa la calidad del análisis basado en el guion y el perfil de marca.
        """
        prompt = f"""
        Actúa como un Experto en Auditoría de Contenido IA. Tu tarea es evaluar el trabajo de otro sistema de IA (ScriptDNA).
        
        PERFIL DE MARCA:
        {json.dumps(brand_profile, indent=2)}
        
        GUION EXTRAÍDO:
        {script}
        
        ANÁLISIS GENERADO:
        {json.dumps(analysis, indent=2)}
        
        Evalúa los siguientes puntos (0-10):
        1. Fidelidad: ¿El análisis refleja realmente el contenido del guion?
        2. Alineación de Marca: ¿Se ajusta el tono y estilo a la marca?
        3. Creatividad: ¿Los ganchos (hooks) son efectivos y no genéricos?
        4. Valor Estratégico: ¿Las recomendaciones son útiles para un equipo de marketing?
        
        Responde exclusivamente en JSON con esta estructura:
        {{
          "puntuaciones": {{
            "fidelidad": 0,
            "alineacion": 0,
            "creatividad": 0,
            "estrategia": 0
          }},
          "critica_constructiva": "tu opinión detallada",
          "veredicto": "APROBADO/RECHAZADO"
        }}
        """.strip()
        
        try:
            # Usamos Gemini para la auditoría (anteriormente Ollama para ahorro local)
            response = ai_provider_service.generate_json(prompt, provider="gemini")
            return response
        except Exception as e:
            return {"error": str(e), "veredicto": "ERROR"}

qa_judge = QAJudge()

if __name__ == "__main__":
    # Prueba rápida con datos ficticios o del Vault
    print("Auditoría de prueba...")
    # ... cargar datos si es necesario ...
