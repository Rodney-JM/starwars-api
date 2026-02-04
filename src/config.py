import os
from dotenv import load_dotenv

# Carregando as variaveis de ambiente
load_dotenv()

class Config:
    SWAPI_BASE_URL = os.getenv("SWAPI_BASE_URL")
    SWAPI_TIMEOUT: int = 10
    SWAPI_MAX_RETRIES: int = 3

    JWT_SECRET = os.getenv("JWT_SECRET", "sua-chave-super-secret")

    CACHE_TTL = 300

    JWT_EXPIRATION = 86400
    API_KEY = os.getenv("API_KEY")

    DEFAULT_LIMIT: int = 10