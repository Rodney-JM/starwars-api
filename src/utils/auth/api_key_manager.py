from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeyManager:
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        valid_keys = [
            Config.API_KEY
        ]

        is_valid = api_key in valid_keys

        if is_valid:
            logger.info("API KEY validada com sucesso")
        else:
            logger.warning(f"Tentativa de uso de API Key inválida: {api_key[:10]}...")

        return is_valid