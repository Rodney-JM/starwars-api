from pydantic import BaseModel
from typing import List, Optional

class Film(BaseModel):
    title: str
    episode_id: int
    opening_crawl: Optional[str] = "Unknown"
    director: str
    producer: str
    release_date: Optional[str] = "Unknown"
    characters: List[str] = []
    planets: List[str] = []
    starships: List[str] = []
    vehicles: List[str] = []
    species: List[str] = []
    url: Optional[str] = "Unknown"
