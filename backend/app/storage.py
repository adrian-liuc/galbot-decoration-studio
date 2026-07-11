import hashlib
import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent

CACHE_DIR = BACKEND_DIR / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = BACKEND_DIR / "assets"


def params_hash(template_id: str, params: dict) -> str:
    payload = json.dumps({"template_id": template_id, "params": params}, sort_keys=True)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def cache_path(design_id: int, params_key: str, suffix: str) -> Path:
    return CACHE_DIR / f"design_{design_id}_{params_key}.{suffix}"
