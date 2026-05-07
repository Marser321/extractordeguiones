import os
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _default_vault_root() -> Path:
    if os.getenv("VAULT_ROOT"):
        return Path(os.getenv("VAULT_ROOT", ""))
    if os.getenv("VERCEL"):
        return Path("/tmp/scriptdna-vault")
    return BASE_DIR / "Vault"

class Settings(BaseSettings):
    PROJECT_NAME: str = "ScriptDNA Orchestrator API"
    VAULT_ROOT: Path = _default_vault_root()
    
    # Gemini Settings (Primary Provider)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEYS: str = os.getenv("GEMINI_API_KEYS", "") # Comma separated list of keys
    GEMINI_DEFAULT_MODEL: str = "gemini-flash-latest"
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"
    
    # AI Pipeline Configuration
    AI_DEFAULT_PROVIDER: str = "gemini"
    AI_FALLBACK_PROVIDER: str = "gemini" # Fallback within Gemini keys if possible
    DEVELOPER_MODE: bool = os.getenv("DEVELOPER_MODE", "false").lower() == "true"
    
    # Ollama Settings (Developer/Local Tooling)
    OLLAMA_BASE_URL: str = "http://localhost:11434/api"
    OLLAMA_DEFAULT_MODEL: str = "llama3"
    
    USE_CLOUD_PIPELINE: bool = True # Cambiar a False para usar Whisper local

    # Whisper Settings
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "small")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "auto") # "auto", "cpu", "cuda"

    # InsForge Settings
    INSFORGE_BASE_URL: str = os.getenv("INSFORGE_BASE_URL", "https://36ssbmb8.us-east.insforge.app")
    INSFORGE_ANON_KEY: str = os.getenv("INSFORGE_ANON_KEY", "")

    class Config:
        env_file = str(BASE_DIR / ".env")
        extra = "ignore"

settings = Settings()
