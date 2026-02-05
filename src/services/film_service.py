import sys
import os
import logging
from typing import Any, Dict, List, Optional

from config import Config
from .swapi.swapi_manager import SwapiManager
from .swapi.utils import extract_id_from_url
from ..schemas.film import Film

class FilmService:
    def __init__(self, swapi_service: Optional[SwapiManager] = None):
        self.swapi = swapi_service or SwapiManager()

    def get_films(
        self,
        search: Optional[str] = None,
        title: Optional[str] = None,
        director: Optional[str] = None,
        episode_id: Optional[int] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        page: int = 1,
        limit: int = Config.DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        if search:
            raw = self.swapi.fetch("films", {"search": search})
            items = raw.get("results", [])
        else:
            items = self.swapi.fetch_all("films")

        films = [Film(**item) for item in items]
        films = self._filter(films, title=title, director=director, episode_id=episode_id)
        films = self._sort(films, sort_by=sort_by, order=order)

        total = len(films)
        total_pages = max(1, (total + limit - 1) // limit)
        start = (page - 1) * limit
        page_data = films[start : start + limit]

        return {
            "data": [f.model_dump() for f in page_data],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }

    def get_film_by_id(self, film_id: int) -> Dict[str, Any]:
        data = self.swapi.fetch_by_id("films", film_id)
        return Film(**data).model_dump()

    def get_film_characters(self, film_id: int) -> Dict[str, Any]:
        film_data = self.swapi.fetch_by_id("films", film_id)
        film = Film(**film_data)

        characters = []
        for char_url in film.characters:
            char_data = self.swapi.fetch_by_url(char_url)
            characters.append(
                {
                    "id": extract_id_from_url(char_url),
                    "name": char_data.get("name"),
                    "gender": char_data.get("gender"),
                    "birth_year": char_data.get("birth_year"),
                }
            )

        return {
            "film": {"id": film_id, "title": film.title, "episode_id": film.episode_id},
            "characters": characters,
            "total_characters": len(characters),
        }

    def get_film_planets(self, film_id: int) -> Dict[str, Any]:
        film_data = self.swapi.fetch_by_id("films", film_id)
        film = Film(**film_data)

        planets = []
        for planet_url in film.planets:
            planet_data = self.swapi.fetch_by_url(planet_url)
            planets.append(
                {
                    "id": extract_id_from_url(planet_url),
                    "name": planet_data.get("name"),
                    "climate": planet_data.get("climate"),
                    "terrain": planet_data.get("terrain"),
                }
            )

        return {
            "film": {"id": film_id, "title": film.title, "episode_id": film.episode_id},
            "planets": planets,
            "total_planets": len(planets),
        }

    def get_film_starships(self, film_id: int) -> Dict[str, Any]:
        film_data = self.swapi.fetch_by_id("films", film_id)
        film = Film(**film_data)

        starships = []
        for ship_url in film.starships:
            ship_data = self.swapi.fetch_by_url(ship_url)
            starships.append(
                {
                    "id": extract_id_from_url(ship_url),
                    "name": ship_data.get("name"),
                    "model": ship_data.get("model"),
                    "starship_class": ship_data.get("starship_class"),
                }
            )

        return {
            "film": {"id": film_id, "title": film.title, "episode_id": film.episode_id},
            "starships": starships,
            "total_starships": len(starships),
        }

    @staticmethod
    def _filter(
        films: List[Film],
        title: Optional[str] = None,
        director: Optional[str] = None,
        episode_id: Optional[int] = None,
    ) -> List[Film]:
        result = films

        if title:
            title_lower = title.lower()
            result = [f for f in result if title_lower in f.title.lower()]

        if director:
            director_lower = director.lower()
            result = [f for f in result if director_lower in f.director.lower()]

        if episode_id is not None:
            result = [f for f in result if f.episode_id == episode_id]

        return result

    @staticmethod
    def _sort(
        films: List[Film],
        sort_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[Film]:
        if not sort_by:
            return films

        reverse = order.lower() == "desc"

        def sort_key(f: Film):
            value = getattr(f, sort_by, "")
            if sort_by == "episode_id":
                return value
            return str(value).lower()

        return sorted(films, key=sort_key, reverse=reverse)