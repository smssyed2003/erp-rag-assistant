import json
import os
from pathlib import Path


def backend_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Environment variable '{key}' is required but was not found."
        )

    return value


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())
