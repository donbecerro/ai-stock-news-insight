import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str = "") -> List[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Stock News Insight API"
    app_env: str = os.getenv("APP_ENV", "local")

    cors_origins: List[str] = None

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_openai_api_version: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
    )

    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")

    def __post_init__(self):
        if self.cors_origins is None:
            object.__setattr__(
                self,
                "cors_origins",
                _csv_env(
                    "CORS_ORIGINS",
                    "http://localhost:3000,http://127.0.0.1:3000",
                ),
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
