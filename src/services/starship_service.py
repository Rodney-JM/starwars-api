import logging
from typing import Any, Dict, List, Optional
from config import Config
from .swapi.swapi_manager import SwapiManager
from .swapi.utils import extract_id_from_url
from ..schemas.starship import Starship

logger = logging.getLogger(__name__)

class StarshipService:
    def __init__(self, swapi_service: Optional[SwapiManager] = None):
        self.swapi = swapi_service or SwapiManager()

    def get_starships(
        self,
        search: Optional[str] = None,
        name: Optional[str] = None,
        model: Optional[str] = None,
        manufacturer: Optional[str] = None,
        starship_class: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        page: int = 1,
        limit: int = Config.DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        if search:
            raw = self.swapi.fetch("starships", {"search": search})
            items = raw.get("results", [])
        else:
            items = self.swapi.fetch_all("starships")

        starships = [Starship(**item) for item in items]
        starships = self._filter(
            starships,
            name=name,
            model=model,
            manufacturer=manufacturer,
            starship_class=starship_class,
        )
        starships = self._sort(starships, sort_by=sort_by, order=order)

        total = len(starships)
        total_pages = max(1, (total + limit - 1) // limit)
        start = (page - 1) * limit
        page_data = starships[start : start + limit]

        return {
            "data": [s.model_dump() for s in page_data],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }

    def get_starship_by_id(self, starship_id: int) -> Dict[str, Any]:
        data = self.swapi.fetch_by_id("starships", starship_id)
        return Starship(**data).model_dump()

    def get_starship_pilots(self, starship_id: int) -> Dict[str, Any]:
        starship_data = self.swapi.fetch_by_id("starships", starship_id)
        starship = Starship(**starship_data)

        pilots = []
        for pilot_url in starship.pilots:
            pilot_data = self.swapi.fetch_by_url(pilot_url)
            pilots.append(
                {
                    "id": extract_id_from_url(pilot_url),
                    "name": pilot_data.get("name"),
                    "gender": pilot_data.get("gender"),
                    "birth_year": pilot_data.get("birth_year"),
                    "homeworld": pilot_data.get("homeworld"),
                }
            )

        return {
            "starship": {
                "id": starship_id,
                "name": starship.name,
                "model": starship.model,
            },
            "pilots": pilots,
            "total_pilots": len(pilots),
        }

    def get_starship_films(self, starship_id: int) -> Dict[str, Any]:
        starship_data = self.swapi.fetch_by_id("starships", starship_id)
        starship = Starship(**starship_data)

        films = []
        for film_url in starship.films:
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
            "starship": {"id": starship_id, "name": starship.name},
            "films": films,
            "total_films": len(films),
        }

    @staticmethod
    def _filter(
        starships: List[Starship],
        name: Optional[str] = None,
        model: Optional[str] = None,
        manufacturer: Optional[str] = None,
        starship_class: Optional[str] = None,
    ) -> List[Starship]:
        result = starships

        if name:
            name_lower = name.lower()
            result = [s for s in result if name_lower in s.name.lower()]

        if model:
            model_lower = model.lower()
            result = [s for s in result if model_lower in s.model.lower()]

        if manufacturer:
            manufacturer_lower = manufacturer.lower()
            result = [s for s in result if manufacturer_lower in s.manufacturer.lower()]

        if starship_class:
            class_lower = starship_class.lower()
            result = [s for s in result if class_lower in s.starship_class.lower()]

        return result

    @staticmethod
    def _sort(
        starships: List[Starship],
        sort_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[Starship]:
        if not sort_by:
            return starships

        reverse = order.lower() == "desc"

        numeric_fields = {"cost_in_credits", "length", "crew", "passengers"}

        def sort_key(s: Starship):
            value = getattr(s, sort_by, "")
            if sort_by in numeric_fields:
                try:
                    return float(str(value).replace(",", ""))
                except (ValueError, AttributeError):
                    return float("inf")
            return str(value).lower()

        return sorted(starships, key=sort_key, reverse=reverse)