"""Cache for WDS records and Gaia cone search results."""

import pickle
import re
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"


def _cache_key(identifier: str, components: str) -> str:
    identifier = identifier.strip().upper().replace(" ", "")
    components = components.upper()
    safe = re.sub(r"[^A-Z0-9+\-]", "_", f"{identifier}_{components}")
    return safe


def _cache_path(identifier: str, components: str) -> Path:
    return CACHE_DIR / f"{_cache_key(identifier, components)}.pkl"


def load(identifier: str, components: str):
    """Return (record, coords, results) from cache, or None if not cached."""
    path = _cache_path(identifier, components)
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def save(identifier: str, components: str, record, coords, results):
    """Save (record, coords, results) to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(identifier, components)
    with open(path, "wb") as f:
        pickle.dump((record, coords, results), f)
