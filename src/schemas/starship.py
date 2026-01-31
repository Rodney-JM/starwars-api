from pydantic import BaseModel
from typing import List, Optional

class Starship(BaseModel):
    name: str = "Unknown"
    model: Optional[str] = "Unknown"
    manufacturer: Optional[str] = "Unknown"
    cost_in_credits: Optional[int] = "Unknown"
    length: Optional[int] = "Unknown"
    max_atmosphering_speed: Optional[str] = "Unknown"
    crew: Optional[int] = "Unknown"
    passengers: Optional[int] = "Unknown"
    cargo_capacity: Optional[int] = "Unknown"
    consumables: Optional[str] = "Unknown"
    hyperdrive_rating: Optional[float] = "Unknown"
    MGLT: Optional[int] = "Unknown"
    starship_class: Optional[str] = "Unknown"
    pilots: List[str] = None
    films: List[str] = "Unknown"
    url: Optional[str] = "Unknown"