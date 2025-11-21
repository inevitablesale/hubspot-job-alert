from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    DOMAINS_FILE_PATH: str
    PORT: int = 8000
    HUBSPOT_ROLE_KEYWORDS: List[str] = Field(
        default_factory=lambda: [
            "hubspot",
            "marketing ops",
            "revops",
            "revenue operations",
            "crm manager",
            "marketing operations",
        ]
    )
    HUBSPOT_EXCLUDE_KEYWORDS: List[str] = Field(
        default_factory=lambda: ["warehouse", "driver", "cashier", "retail"]
    )
    CRAWLER_MAX_DEPTH: int = 3
    CRAWLER_MAX_PAGES_PER_DOMAIN: int = 25
    CRAWLER_MAX_PAGINATION_PAGES: int = 3
    CRAWLER_URL_MAX_LENGTH: int = 200
    CRAWLER_EXCLUDE_PATH_PREFIXES: List[str] = Field(
        default_factory=lambda: [
            "/wp-admin",
            "/private",
            "/checkout",
            "/cart",
            "/login",
            "/blog",
            "/wp-login.php",
            "/terms",
            "/terms-and-conditions",
            "/about",
            "/privacy",
            "/privacy-policy",
            "/press",
        ]
    )

    @validator("HUBSPOT_ROLE_KEYWORDS", "HUBSPOT_EXCLUDE_KEYWORDS", pre=True)
    def _split_keywords(cls, value):
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return [item.lower() for item in value]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
