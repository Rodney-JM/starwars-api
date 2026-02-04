from typing import Any, Dict, List, Optional
import sys
import os
import logging
from config import Config
from .swapi.swapi_manager import SwapiManager
from .swapi.utils import extract_id_from_url
from ..schemas.character import Character

logger = logging.getLogger(__name__)

class CharacterService:
    def __init__(self, swapi_service: Optional[SwapiManager] = None):
        self.swapi_service = swapi_service or SwapiManager()

    def get_characters(
            self,
            search: Optional[str] = None,
            name: Optional[str] = None,
            gender: Optional[str] = None,
            birth_year: Optional[str] = None,
            sort_by: Optional[str] = None,
            order: str = "asc",
            page: int = 1,
            limit: int = Config.DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        if search:
            raw = self.swapi_service.fetch("people", {"search": search})
            items = raw.get("results", [])
        else:
            items = self.swapi_service.fetch_all("people")

        #conversao para models
        characters = [Character(**item) for item in items]
        #filtragem
        characters = self._filter(characters, name=name, gender=gender, birth_year=birth_year)

        #ordenaçao
        characters = self._sort(characters, sort_by=sort_by, order=order)

        #paginaçao
        total = len(characters)
        total_pages = max(1, (total + limit - 1) // limit)
        start = (page - 1) * limit
        end = start + limit
        page_data = characters[start:end]

        return {
            "data": [c.model_dump() for c in page_data],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }

    def get_character_by_id(self, character_id: int) -> Dict[str, Any]:
        data = self.swapi_service.fetch_by_id("people", character_id)
        return Character(**data).model_dump()

    def get_character_films(self, character_id: int) -> Dict[str, Any]:
        character_data = self.swapi_service.fetch_by_id("people", character_id)
        character = Character(**character_data)

        films = []
        for film_url in character.films:
            film_data = self.swapi_service.fetch_by_url(film_url)
            films.append(
                {
                    "id": extract_id_from_url(film_url),
                    "title": film_data.get("title"),
                    "episode_id": film_data.get("episode_id"),
                    "release_date": film_data.get("release_date"),
                    "director": film_data.get("director"),
                }
            )

        return {
            "character": {"id": character_id, "name": character.name},
            "films": films,
            "total_films": len(films),
        }


    def get_character_starships(self, character_id: int) -> Dict[str, Any]:
        character_data = self.swapi_service.fetch_by_id("people", character_id)
        character = Character(**character_data)

        starships = []
        for ship_url in character.starships:
            ship_data = self.swapi_service.fetch_by_url(ship_url)
            starships.append(
                {
                    "id": extract_id_from_url(ship_url),
                    "name": ship_data.get("name"),
                    "model": ship_data.get("model"),
                    "manufacturer": ship_data.get("manufacturer"),
                    "starship_class": ship_data.get("starship_class"),
                }
            )

        return {
            "character": {"id": character_id, "name": character.name},
            "starships": starships,
            "total_starships": len(starships),
        }


    def get_character_homeworld(self, character_id: int) -> Dict[str, Any]:
        character_data = self.swapi_service.fetch_by_id("people", character_id)
        character = Character(**character_data)

        planet_data = self.swapi_service.fetch_by_url(character.homeworld)

        return {
            "character": {"id": character_id, "name": character.name},
            "homeworld": {
                "id": extract_id_from_url(character.homeworld),
                "name": planet_data.get("name"),
                "climate": planet_data.get("climate"),
                "terrain": planet_data.get("terrain"),
                "population": planet_data.get("population"),
                "gravity": planet_data.get("gravity"),
            },
        }

    @staticmethod
    def _filter(
            characters: List[Character],
            name: Optional[str] = None,
            gender: Optional[str] = None,
            birth_year: Optional[str] = None,
    ) -> List[Character]:
        result = characters

        if name:
            name_lower = name.lower()
            result = [c for c in result if name_lower in c.name.lower()]

        if gender:
            gender_lower = gender.lower()
            result = [c for c in result if c.gender.lower() == gender_lower]

        if birth_year:
            result = [c for c in result if c.birth_year.lower() == birth_year.lower()]

        return result

    @staticmethod
    def _sort(
            characters: List[Character],
            sort_by: Optional[str] = None,
            order: str = "asc",
    ) -> List[Character]:
        if not sort_by:
            return characters

        reverse = order.lower() == "desc"

        numeric_fields = {"height", "mass"}

        def sort_key(c: Character):
            value = getattr(c, sort_by, "")
            if sort_by in numeric_fields:
                try:
                    return float(value.replace(",", ""))
                except (ValueError, AttributeError):
                    return float("inf")
            return str(value).lower()

        return sorted(characters, key=sort_key, reverse=reverse)

    @staticmethod
    def _paginate(items: list, page: int, limit: int) -> list:
        start = (page - 1) * limit
        return items[start: start + limit]