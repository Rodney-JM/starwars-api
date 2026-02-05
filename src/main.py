import sys
import os
import logging

import functions_framework
from flask import request, jsonify

from config import Config
from .utils.auth.jwt_manager import TokenManager
from .utils.validators.film_validator import FilmValidator
from .utils.validators.character_validator import CharacterValidator
from .utils.validators.planet_validator import PlanetValidator
from .utils.validators.starship_validator import StarshipValidator
from .services.character_service import CharacterService
from .services.planet_service import PlanetService
from .services.starship_service import StarshipService
from .services.film_service import FilmService
from .services.swapi.exceptions import SWAPIError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

#singletons da app
character_service = CharacterService()
planet_service = PlanetService()
starship_service = StarshipService()
film_service = FilmService()

#entrypoint
@functions_framework.http
def starwars_api(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-API-Key, Authorization",
    }

    if request.method == "OPTIONS":
        return "", 204, headers

    path = request.path.rstrip("/")
    try:
        if path == "/auth/login" and request.method == "POST":
            response, status = handle_login()
            return jsonify(response), status, headers

        if path == "/auth/refresh" and request.method == "POST":
            response, status = handle_refresh()
            return jsonify(response), status, headers

        if path in ("", "/", "/health"):
            response, status = handle_health()
            return jsonify(response), status, headers

        auth_error = validate_auth(request)
        if auth_error:
            return jsonify(auth_error), 401, headers

        if path == "/characters" and request.method == "GET":
            response, status = handle_get_characters()
            return jsonify(response), status, headers

        if path.startswith("/characters/") and request.method == "GET":
            # Extrai o ID ou sub-recurso da URL
            parts = path.split("/")
            resource_id = parts[2] if len(parts) > 2 else None
            sub_resource = parts[3] if len(parts) > 3 else None

            response, status = handle_character_detail(resource_id, sub_resource)
            return jsonify(response), status, headers

        if path == "/planets" and request.method == "GET":
            response, status = handle_get_planets()
            return jsonify(response), status, headers

        if path.startswith("/planets/") and request.method == "GET":
            parts = path.split("/")
            resource_id = parts[2] if len(parts) > 2 else None
            sub_resource = parts[3] if len(parts) > 3 else None

            response, status = handle_planet_detail(resource_id, sub_resource)
            return jsonify(response), status, headers

        if path == "/starships" and request.method == "GET":
            response, status = handle_get_starships()
            return jsonify(response), status, headers

        if path.startswith("/starships/") and request.method == "GET":
            parts = path.split("/")
            resource_id = parts[2] if len(parts) > 2 else None
            sub_resource = parts[3] if len(parts) > 3 else None

            response, status = handle_starship_detail(resource_id, sub_resource)
            return jsonify(response), status, headers

        if path == "/films" and request.method == "GET":
            response, status = handle_get_films()
            return jsonify(response), status, headers

        if path.startswith("/films/") and request.method == "GET":
            parts = path.split("/")
            resource_id = parts[2] if len(parts) > 2 else None
            sub_resource = parts[3] if len(parts) > 3 else None

            response, status = handle_film_detail(resource_id, sub_resource)
            return jsonify(response), status, headers

        if path == "/search" and request.method == "GET":
            response, status = handle_global_search()
            return jsonify(response), status, headers

        return jsonify({"error": True, "message": f"Endpoint '{path}' não encontrado", "code": 404}), 404, headers

    except SWAPIError as e:
        logger.error(f"Erro SWAPI: {e.message}")
        return jsonify({"error": True, "message": e.message, "code": e.status_code}), e.status_code, headers
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return (
            jsonify({"error": True, "message": "Erro interno do servidor", "code": 500}),
            500,
            headers,
        )

def validate_auth(req) -> dict | None:
    api_key = req.headers.get("X-API-Key")
    if api_key:
        if api_key == Config.API_KEY:
            return None
        return {"error": True, "message": "API Key inválida", "code": 401}

    auth_header = req.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            try:
                TokenManager.validate_token(parts[1])
                return None
            except Exception:
                return {"error": True, "message": "Token inválido ou expirado", "code": 401}

    return {"error": True, "message": "Autenticação necessária. Use X-API-Key ou Authorization: Bearer <token>", "code": 401}

def handle_login():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    password = body.get("password")

    DEMO_USERS = {
        "admin": "admin123",
        "user": "user123",
    }

    if username not in DEMO_USERS or DEMO_USERS[username] != password:
        return {"error": True, "message": "Usuário ou senha inválidos", "code": 401}, 401

    token = TokenManager.generate_token(username, {"role": "admin" if username == "admin" else "user"})

    return {
        "token": token,
        "token_type": "Bearer",
        "expires_in": Config.JWT_EXPIRATION,
        "message": "Login bem-sucedido",
    }, 200


def handle_refresh():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": True, "message": "Token não fornecido", "code": 401}, 401

    old_token = auth_header.split()[1]
    try:
        new_token = TokenManager.refresh_token(old_token)
        return {
            "token": new_token,
            "token_type": "Bearer",
            "expires_in": Config.JWT_EXPIRATION,
            "message": "Token renovado",
        }, 200
    except Exception:
        return {"error": True, "message": "Token inválido ou expirado", "code": 401}, 401

def handle_health():
    return {
        "status": "ok",
        "message": "Star Wars API está funcionando!",
        "version": "1.0.0",
        "endpoints": {
            "auth": ["/auth/login", "/auth/refresh"],
            "characters": ["/characters", "/characters/{id}", "/characters/{id}/films", "/characters/{id}/starships", "/characters/{id}/homeworld"],
            "planets": ["/planets", "/planets/{id}", "/planets/{id}/residents", "/planets/{id}/films"],
            "starships": ["/starships", "/starships/{id}", "/starships/{id}/pilots", "/starships/{id}/films"],
            "films": ["/films", "/films/{id}", "/films/{id}/characters", "/films/{id}/planets", "/films/{id}/starships"],
            "search": ["/search?q=<termo>"],
        },
    }, 200

def handle_get_characters():
    params = request.args.to_dict()

    # Validação
    errors = CharacterValidator.validate(params)
    if errors:
        return {"error": True, "message": "Erros de validação", "errors": errors, "code": 400}, 400

    result = character_service.get_characters(
        search=params.get("search"),
        name=params.get("name"),
        gender=params.get("gender"),
        birth_year=params.get("birth_year"),
        sort_by=params.get("sort_by"),
        order=params.get("order", "asc"),
        page=int(params.get("page", Config.DEFAULT_PAGE)),
        limit=int(params.get("limit", Config.DEFAULT_LIMIT)),
    )

    return result, 200


def handle_character_detail(resource_id, sub_resource):
    try:
        char_id = int(resource_id)
    except (ValueError, TypeError):
        return {"error": True, "message": "ID deve ser um número inteiro", "code": 400}, 400

    if sub_resource is None:
        return character_service.get_character_by_id(char_id), 200

    if sub_resource == "films":
        return character_service.get_character_films(char_id), 200

    if sub_resource == "starships":
        return character_service.get_character_starships(char_id), 200

    if sub_resource == "homeworld":
        return character_service.get_character_homeworld(char_id), 200

    return {"error": True, "message": f"Sub-recurso '{sub_resource}' não encontrado", "code": 404}, 404

def handle_get_planets():
    #GET /planets — lista com filtros, ordenação, paginação.
    params = request.args.to_dict()

    errors = PlanetValidator.validate(params)
    if errors:
        return {"error": True, "message": "Erros de validação", "errors": errors, "code": 400}, 400

    result = planet_service.get_planets(
        search=params.get("search"),
        name=params.get("name"),
        climate=params.get("climate"),
        terrain=params.get("terrain"),
        sort_by=params.get("sort_by"),
        order=params.get("order", "asc"),
        page=int(params.get("page", Config.DEFAULT_PAGE)),
        limit=int(params.get("limit", Config.DEFAULT_LIMIT)),
    )

    return result, 200


def handle_planet_detail(resource_id, sub_resource):
    try:
        planet_id = int(resource_id)
    except (ValueError, TypeError):
        return {"error": True, "message": "ID deve ser um número inteiro", "code": 400}, 400

    if sub_resource is None:
        return planet_service.get_planet_by_id(planet_id), 200

    if sub_resource == "residents":
        return planet_service.get_planet_residents(planet_id), 200

    if sub_resource == "films":
        return planet_service.get_planet_films(planet_id), 200

    return {"error": True, "message": f"Sub-recurso '{sub_resource}' não encontrado", "code": 404}, 404


def handle_get_starships():
    # lista com filtros, ordenação, paginação.
    params = request.args.to_dict()

    errors = StarshipValidator.validate(params)
    if errors:
        return {"error": True, "message": "Erros de validação", "errors": errors, "code": 400}, 400

    result = starship_service.get_starships(
        search=params.get("search"),
        name=params.get("name"),
        model=params.get("model"),
        manufacturer=params.get("manufacturer"),
        starship_class=params.get("starship_class"),
        sort_by=params.get("sort_by"),
        order=params.get("order", "asc"),
        page=int(params.get("page", Config.DEFAULT_PAGE)),
        limit=int(params.get("limit", Config.DEFAULT_LIMIT)),
    )

    return result, 200


def handle_starship_detail(resource_id, sub_resource):
    #GET /starships/{id} e sub-recursos.
    try:
        starship_id = int(resource_id)
    except (ValueError, TypeError):
        return {"error": True, "message": "ID deve ser um número inteiro", "code": 400}, 400

    if sub_resource is None:
        return starship_service.get_starship_by_id(starship_id), 200

    if sub_resource == "pilots":
        return starship_service.get_starship_pilots(starship_id), 200

    if sub_resource == "films":
        return starship_service.get_starship_films(starship_id), 200

    return {"error": True, "message": f"Sub-recurso '{sub_resource}' não encontrado", "code": 404}, 404

def handle_get_films():
    #GET /films — lista com filtros, ordenação, paginação.
    params = request.args.to_dict()

    errors = FilmValidator.validate(params)
    if errors:
        return {"error": True, "message": "Erros de validação", "errors": errors, "code": 400}, 400

    episode_id = params.get("episode_id")
    if episode_id is not None:
        try:
            episode_id = int(episode_id)
        except ValueError:
            return {"error": True, "message": "episode_id deve ser um número inteiro", "code": 400}, 400

    result = film_service.get_films(
        search=params.get("search"),
        title=params.get("title"),
        director=params.get("director"),
        episode_id=episode_id,
        sort_by=params.get("sort_by"),
        order=params.get("order", "asc"),
        page=int(params.get("page", Config.DEFAULT_PAGE)),
        limit=int(params.get("limit", Config.DEFAULT_LIMIT)),
    )

    return result, 200


def handle_film_detail(resource_id, sub_resource):
    #GET /films/{id} e sub-recursos.
    try:
        film_id = int(resource_id)
    except (ValueError, TypeError):
        return {"error": True, "message": "ID deve ser um número inteiro", "code": 400}, 400

    if sub_resource is None:
        return film_service.get_film_by_id(film_id), 200

    if sub_resource == "characters":
        return film_service.get_film_characters(film_id), 200

    if sub_resource == "planets":
        return film_service.get_film_planets(film_id), 200

    if sub_resource == "starships":
        return film_service.get_film_starships(film_id), 200

    return {"error": True, "message": f"Sub-recurso '{sub_resource}' não encontrado", "code": 404}, 404

def handle_global_search():
    query = request.args.get("q")
    search_type = request.args.get("type", "all").lower()

    if not query or len(query) < 2:
        return {"error": True, "message": "Parâmetro 'q' é obrigatório e deve ter pelo menos 2 caracteres", "code": 400}, 400

    valid_types = ("all", "characters", "planets", "starships", "films")
    if search_type not in valid_types:
        return {"error": True, "message": f"'type' deve ser um de: {', '.join(valid_types)}", "code": 400}, 400

    results = {}

    if search_type in ("all", "characters"):
        char_result = character_service.get_characters(search=query, limit=5)
        results["characters"] = char_result["data"]

    if search_type in ("all", "planets"):
        planet_result = planet_service.get_planets(search=query, limit=5)
        results["planets"] = planet_result["data"]

    if search_type in ("all", "starships"):
        ship_result = starship_service.get_starships(search=query, limit=5)
        results["starships"] = ship_result["data"]

    if search_type in ("all", "films"):
        film_result = film_service.get_films(search=query, limit=5)
        results["films"] = film_result["data"]

    # Conta total de resultados
    total = sum(len(v) for v in results.values())

    return {
        "query": query,
        "type": search_type,
        "total_results": total,
        "results": results,
    }, 200
