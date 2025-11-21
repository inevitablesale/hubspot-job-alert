from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


SECRET_DOMAINS_PATH = Path("/etc/secrets/DOMAINS_FILE")


class Settings(BaseSettings):
    DOMAINS_FILE_PATH: str = (
        str(SECRET_DOMAINS_PATH)
        if SECRET_DOMAINS_PATH.exists()
        else "domains.json"
    )
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

    @field_validator(
        "HUBSPOT_ROLE_KEYWORDS", "HUBSPOT_EXCLUDE_KEYWORDS", mode="before"
    )
    @classmethod
    def _split_keywords(cls, value):
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return [item.lower() for item in value]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
