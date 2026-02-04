from typing import Optional

def extract_id_from_url(url: str) -> Optional[int]:
    if not url:
        return None

    try:
        return int(url.rstrip("/").split("/")[-1])
    except (ValueError, IndexError):
        return None