from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Character(BaseModel):
    name: str = "Unknown"
    height: Optional[str] = None
    mass: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    birth_year: Optional[str] = None
    gender: Optional[str] = None
    homeworld: Optional[str] = None
    films: List[str] = []
    species: List[str] = []
    vehicles: List[str] = []
    starships: List[str] = []