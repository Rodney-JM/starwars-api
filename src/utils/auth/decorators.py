import jwt
import logging
from flask import jsonify, request
from functools import wraps
from api_key_manager import APIKeyManager
from jwt_manager import TokenManager
from exceptions import AuthenticationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            logger.warning("Requisição sem API Key")
            return jsonify({
                "error": "API Key não fornecida",
                "message": "Inclua o header X-API-Key na requisição"
            }), 401

        if not APIKeyManager.validate_api_key(api_key):
            logger.warning(f"API Key inválida recebida")
            return jsonify({
                "error": "API Key Inválida",
                "message": "A chave fornecida não é válida"
            }), 401

        return f(*args, **kwargs)

    return decorated_function

def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning("Requisição sem token JWT")
            return jsonify({
                "error": "Token não fornecido",
                "message": "Inclua o header Authorization: Bearer <token>"
            }), 401

        #validar o formato
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Formato de Authorization inválido")
            return jsonify({
                "error": "Formato de token inválido",
                "message": "Use o formato: Authorization: Bearer <token>"
            }), 401

        token = parts[1]

        try:
            payload = TokenManager.validate_token(token)

            request.user_id = payload.get("sub")
            request.user_claims = payload

            #exec a func principal
            return f(*args, **kwargs)
        except AuthenticationError as e:
            return jsonify({
                "error": "Autenticação falhou",
                "message": e.message
            }), e.status_code

    return decorated_function

def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key and APIKeyManager.validate_api_key(api_key):
            request.authenticated = True
            request.auth_method = ('api_key')

            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) != 2 and parts[0].lower() != "bearer":
                try:
                    payload = TokenManager.validate_token(parts[1])
                    request.authenticated = True
                    request.auth_method = 'jwt'
                    request.user_id = payload.get("sub")
                    request.user_claims = payload
                    return f(*args, **kwargs)
                except AuthenticationError:
                    pass
        request.authenticated = False
        request.auth_method = None
        return f(*args, **kwargs)
    return decorated_function