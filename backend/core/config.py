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
    
    # Qwen / DashScope Settings (Primary Provider)
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_API_KEYS: str = os.getenv("DASHSCOPE_API_KEYS", "") # Comma separated list of keys
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_API_KEYS: str = os.getenv("QWEN_API_KEYS", "") # Optional alias list
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope-us.aliyuncs.com/compatible-mode/v1")
    QWEN_FAST_MODEL: str = os.getenv("QWEN_FAST_MODEL", "qwen-flash")
    QWEN_QUALITY_MODEL: str = os.getenv("QWEN_QUALITY_MODEL", "qwen-plus")
    QWEN_DEEP_MODEL: str = os.getenv("QWEN_DEEP_MODEL", "qwen-max")
    QWEN_VISION_MODEL: str = os.getenv("QWEN_VISION_MODEL", "qwen-vl-plus")

    # Hugging Face / fal Settings (Open-source-first media layer)
    HF_TOKEN: str = os.getenv("HF_TOKEN", os.getenv("HUGGINGFACE_API_KEY", ""))
    HF_TOKENS: str = os.getenv("HF_TOKENS", os.getenv("HUGGINGFACE_API_KEYS", ""))
    HUGGINGFACE_DEFAULT_TEXT_MODEL: str = os.getenv("HUGGINGFACE_DEFAULT_TEXT_MODEL", "Qwen/Qwen3-8B")
    HUGGINGFACE_DEFAULT_IMAGE_MODEL: str = os.getenv("HUGGINGFACE_DEFAULT_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
    FAL_KEY: str = os.getenv("FAL_KEY", os.getenv("FAL_API_KEY", ""))
    FAL_KEYS: str = os.getenv("FAL_KEYS", os.getenv("FAL_API_KEYS", ""))
    FAL_IMAGE_DEFAULT_MODEL: str = os.getenv("FAL_IMAGE_DEFAULT_MODEL", "fal-ai/flux/schnell")
    FAL_VIDEO_DEFAULT_MODEL: str = os.getenv("FAL_VIDEO_DEFAULT_MODEL", "fal-ai/ltx-video-13b-distilled")

    # Gemini Settings (Optional Secondary Provider)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEYS: str = os.getenv("GEMINI_API_KEYS", "") # Comma separated list of keys
    GEMINI_DEFAULT_MODEL: str = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash")
    GEMINI_PRO_MODEL: str = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")
    
    # OpenRouter Settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_KEYS: str = os.getenv("OPENROUTER_API_KEYS", "") # Comma separated list of keys
    OPENROUTER_DEFAULT_MODEL: str = os.getenv("OPENROUTER_DEFAULT_MODEL", "qwen/qwen3.6-flash")
    
    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEYS: str = os.getenv("GROQ_API_KEYS", "") # Comma separated list of keys
    GROQ_DEFAULT_MODEL: str = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.1-70b-versatile")
    
    # OpenAI Settings (Optional Image Fallback)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_KEYS: str = os.getenv("OPENAI_API_KEYS", "")
    OPENAI_IMAGE_DEFAULT_MODEL: str = os.getenv("OPENAI_IMAGE_DEFAULT_MODEL", "gpt-image-1.5")
    IMAGE_DEFAULT_PROVIDER: str = os.getenv("IMAGE_DEFAULT_PROVIDER", "fal")
    
    # AI Pipeline Configuration
    AI_DEFAULT_PROVIDER: str = os.getenv("AI_DEFAULT_PROVIDER", "qwen")
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
