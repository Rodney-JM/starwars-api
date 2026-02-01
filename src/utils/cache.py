from cachetools import TTLCache
from typing import Any, Optional
from config import Config

_cache = TTLCache(maxsize=100, ttl=Config.CACHE_TTL)

def get_from_cache(key: str) -> Optional[Any]:
    return _cache.get(key)

def set_in_cache(key: str, value: Any) -> None:
    _cache[key] = value

def clear_cache() -> None:
    _cache.clear()

def cache_key(*args , **kwargs) -> str:
    key_parts = [str(arg) for arg in args]

    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}={v}")

    return "_".join(key_parts)