import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

try:
    from services.vault_service import vault_service
    from services.ai_provider_service import ai_provider_service
except ModuleNotFoundError:
    from backend.services.vault_service import vault_service
    from backend.services.ai_provider_service import ai_provider_service

class GlobalBenchmarkingService:
    def __init__(self):
        self.global_vault_path = Path(__file__).resolve().parent.parent / "Vault" / "GlobalIntelligence"
        self.global_vault_path.mkdir(parents=True, exist_ok=True)

    def consolidate_global_intelligence(self, ai_provider: str = "gemini") -> dict:
        """
        Escanea todas las marcas y consolida patrones de éxito globales.
        """
        all_brand_wisdom = []
        
        # 1. Recolectar sabiduría de todas las marcas
        brands = vault_service.list_brands()
        for brand in brands:
            brand_name = brand["brand_name"]
            # Ajustado a la ruta detectada: Vault/Marcas/{brand}/Analisis/sabiduria_marca.json
            path = vault_service.marcas_dir / brand_name / "Analisis" / "sabiduria_marca.json"
            if path.exists():
                wisdom = vault_service.read_json(path)
                if wisdom:
                    wisdom["_brand_source"] = brand_name
                    all_brand_wisdom.append(wisdom)
        
        if not all_brand_wisdom:
            return {"status": "no_data", "message": "No hay suficiente sabiduría de marca consolidada para benchmark."}

        # 2. Sintetizar con IA
        prompt = f"""
        Eres un Arquitecto de Estrategia de Marketing de Alto Nivel. 
        Tu tarea es analizar los aprendizajes de múltiples marcas y destilar el "ScriptDNA Global".
        
        Datos de Marcas:
        {json.dumps(all_brand_wisdom, ensure_ascii=False, indent=2)}
        
        Identifica:
        1. Patrones Ganadores Universales: ¿Qué funciona siempre, independientemente de la marca?
        2. Barreras Comunes: ¿En qué están fallando la mayoría de los análisis?
        3. Evolución del DNA: ¿Hacia dónde debe evolucionar la inteligencia de la app?
        
        Responde exclusivamente en JSON:
        {{
          "scriptdna_global_version": "1.0",
          "patrones_ganadores_globales": ["patrón"],
          "barreras_criticas_sistema": ["barrera"],
          "benchmarking_nichos": {{"nicho": "comportamiento detectado"}},
          "recomendaciones_arquitectura": ["recomendación"]
        }}
        """
        
        print("[Benchmarking] Sintetizando inteligencia global...")
        global_intelligence = ai_provider_service.generate_json(prompt, provider=ai_provider)
        
        # 3. Guardar en el Vault Global
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        vault_service.save_json(self.global_vault_path, f"global_dna_{timestamp}.json", global_intelligence)
        vault_service.save_json(self.global_vault_path, "latest_global_dna.json", global_intelligence)
        
        return global_intelligence

global_benchmarking_service = GlobalBenchmarkingService()
