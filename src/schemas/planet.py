from pydantic import BaseModel
from typing import Optional, List

class Planet(BaseModel):
    name: str = "Unknown"
    rotation_period: Optional[int] = None
    orbital_period: Optional[int] = None
    diameter: Optional[int] = None
    climate: Optional[str] = "Unknown"
    gravity: Optional[str] = "Unknown"
    terrain: Optional[str] = "Unknown"
    surface_water: Optional[float] = "Unknown"
    population: Optional[int] = "Unknown"
    residents: List[str] = []
    films: List[str] = []