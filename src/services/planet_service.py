import logging
from typing import Any, Dict, List, Optional

from config import Config
from .swapi.swapi_manager import SwapiManager
from .swapi.utils import extract_id_from_url
from ..schemas.planet import Planet

logger = logging.getLogger(__name__)
class PlanetService:
    def __init__(self, swapi_service: Optional[SwapiManager] = None):
        self.swapi = swapi_service or SwapiManager()

    def get_planets(
        self,
        search: Optional[str] = None,
        name: Optional[str] = None,
        climate: Optional[str] = None,
        terrain: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        page: int = 1,
        limit: int = Config.DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        if search:
            raw = self.swapi.fetch("planets", {"search": search})
            items = raw.get("results", [])
        else:
            items = self.swapi.fetch_all("planets")

        planets = [Planet(**item) for item in items]
        planets = self._filter(planets, name=name, climate=climate, terrain=terrain)
        planets = self._sort(planets, sort_by=sort_by, order=order)

        total = len(planets)
        total_pages = max(1, (total + limit - 1) // limit)
        start = (page - 1) * limit
        page_data = planets[start : start + limit]

        return {
            "data": [p.model_dump() for p in page_data],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }

    def get_planet_by_id(self, planet_id: int) -> Dict[str, Any]:
        data = self.swapi.fetch_by_id("planets", planet_id)
        return Planet(**data).model_dump()

    def get_planet_residents(self, planet_id: int) -> Dict[str, Any]:
        planet_data = self.swapi.fetch_by_id("planets", planet_id)
        planet = Planet(**planet_data)

        residents = []
        for resident_url in planet.residents:
            resident_data = self.swapi.fetch_by_url(resident_url)
            residents.append(
                {
                    "id": extract_id_from_url(resident_url),
                    "name": resident_data.get("name"),
                    "gender": resident_data.get("gender"),
                    "birth_year": resident_data.get("birth_year"),
                }
            )

        return {
            "planet": {"id": planet_id, "name": planet.name},
            "residents": residents,
            "total_residents": len(residents),
        }

    def get_planet_films(self, planet_id: int) -> Dict[str, Any]:
        planet_data = self.swapi.fetch_by_id("planets", planet_id)
        planet = Planet(**planet_data)

        films = []
        for film_url in planet.films:
            film_data = self.swapi.fetch_by_url(film_url)
            films.append(
                {
                    "id": extract_id_from_url(film_url),
                    "title": film_data.get("title"),
                    "episode_id": film_data.get("episode_id"),
                    "release_date": film_data.get("release_date"),
                }
            )

        return {
            "planet": {"id": planet_id, "name": planet.name},
            "films": films,
            "total_films": len(films),
        }

    @staticmethod
    def _filter(
        planets: List[Planet],
        name: Optional[str] = None,
        climate: Optional[str] = None,
        terrain: Optional[str] = None,
    ) -> List[Planet]:
        result = planets

        if name:
            name_lower = name.lower()
            result = [p for p in result if name_lower in p.name.lower()]

        if climate:
            climate_lower = climate.lower()

            result = [p for p in result if climate_lower in p.climate.lower()]

        if terrain:
            terrain_lower = terrain.lower()
            result = [p for p in result if terrain_lower in p.terrain.lower()]

        return result

    @staticmethod
    def _sort(
        planets: List[Planet],
        sort_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[Planet]:
        if not sort_by:
            return planets

        reverse = order.lower() == "desc"

        numeric_fields = {"population", "diameter"}

        def sort_key(p: Planet):
            value = getattr(p, sort_by, "")
            if sort_by in numeric_fields:
                try:
                    return float(str(value).replace(",", ""))
                except (ValueError, AttributeError):
                    return float("inf")
            return str(value).lower()

        return sorted(planets, key=sort_key, reverse=reverse)