from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    litellm_base_url: str
    skyvern_base_url: str
    memory_db_path: str
    dry_run: bool


def load_settings() -> Settings:
    return Settings(
        litellm_base_url=os.getenv("LITELLM_BASE_URL", "http://litellm:4000"),
        skyvern_base_url=os.getenv("SKYVERN_BASE_URL", "http://skyvern:8000"),
        memory_db_path=os.getenv("MEMORY_DB_PATH", "/data/memory/skyagentos.db"),
        dry_run=os.getenv("SKYAGENT_DRY_RUN", "false").lower() == "true",
    )
