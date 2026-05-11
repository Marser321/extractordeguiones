from pathlib import Path
import os

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_vercel() -> bool:
    return _env_flag("VERCEL")


def _is_cloud() -> bool:
    return _is_vercel() or _env_flag("CLOUD_MODE")


def _default_vault_root() -> Path:
    if os.getenv("VAULT_ROOT"):
        return Path(os.getenv("VAULT_ROOT", ""))
    if _is_cloud():
        return Path("/tmp/scriptdna-vault")
    return BASE_DIR / "Vault"


class Settings(BaseSettings):
    PROJECT_NAME: str = "ScriptDNA Orchestrator API"
    VAULT_ROOT: Path = _default_vault_root()
    IS_VERCEL: bool = _is_vercel()
    IS_CLOUD: bool = _is_cloud()
    
    # Gemini Settings (Primary Provider)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEYS: str = os.getenv("GEMINI_API_KEYS", "") # Comma separated list of keys
    GEMINI_DEFAULT_MODEL: str = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash")
    GEMINI_PRO_MODEL: str = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")
    
    # OpenRouter Settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_KEYS: str = os.getenv("OPENROUTER_API_KEYS", "") # Comma separated list of keys
    OPENROUTER_DEFAULT_MODEL: str = os.getenv("OPENROUTER_DEFAULT_MODEL", "meta-llama/llama-3-8b-instruct:free")
    
    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEYS: str = os.getenv("GROQ_API_KEYS", "") # Comma separated list of keys
    GROQ_DEFAULT_MODEL: str = os.getenv("GROQ_DEFAULT_MODEL", "llama3-70b-8192")
    
    # AI Pipeline Configuration
    AI_DEFAULT_PROVIDER: str = os.getenv("AI_DEFAULT_PROVIDER", "openrouter")
    AI_FALLBACK_PROVIDER: str = os.getenv("AI_FALLBACK_PROVIDER", "openrouter")
    DEVELOPER_MODE: bool = _env_flag("DEVELOPER_MODE")
    
    # Ollama Settings (Developer/Local Tooling)
    OLLAMA_BASE_URL: str = "http://localhost:11434/api"
    OLLAMA_DEFAULT_MODEL: str = "llama3"
    
    USE_CLOUD_PIPELINE: bool = _env_flag("USE_CLOUD_PIPELINE", default=_is_cloud())

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
if settings.IS_CLOUD:
    settings.VAULT_ROOT = Path("/tmp/scriptdna-vault")
