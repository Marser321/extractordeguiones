import requests
import google.generativeai as genai

try:
    from core.config import settings
except ModuleNotFoundError:
    from backend.core.config import settings

class LLMService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL
        
        # Init Gemini si hay API key
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_pro = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.gemini_model = None
            self.gemini_pro = None

    def has_gemini(self) -> bool:
        return self.gemini_model is not None

    def generate_with_ollama(self, prompt: str, model: str = None) -> str:
        """Llama a la API local de Ollama."""
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(f"{self.ollama_url}/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            return f"Error conectando con Ollama: {str(e)}"

    def generate_with_gemini(self, prompt: str, use_pro: bool = False) -> str:
        """Llama a la API de Gemini."""
        if not self.gemini_model:
            return "Error: GEMINI_API_KEY no configurada."
        
        model = self.gemini_pro if use_pro else self.gemini_model
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error conectando con Gemini: {str(e)}"

llm_service = LLMService()
