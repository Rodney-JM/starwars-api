import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config import Config
import jwt
from exceptions import AuthenticationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenManager:
    @staticmethod
    def generate_token(user_id: str, additional_claims: Optional[Dict] = None) -> str:
        try:
            payload = {
                "sub": user_id,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRATION),
                "jti": f"{user_id}_{datetime.utcnow().timestamp()}"
            }

            if additional_claims:
                payload.update(additional_claims)

            token = jwt.encode(
                payload,
                Config.JWT_SECRET,
                algorithm="HS256"
            )

            logger.info(f"Token gerado com sucesso para o usuário: {user_id}")
            return token

        except Exception as e:
            logger.error(f"Erro ao gerar token: {str(e)}")
            raise Exception(f"Falha ao gerar token: {str(e)}")

    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=["HS256"]
            )

            logger.info(f"Token validado com sucesso para usuário: {payload.get('sub')}")

            return payload
        except jwt.ExpiredSignatureError:
            # token expirado
            logger.warning("Tentativa de uso de token expirado")
            raise AuthenticationError("Token expirado", 401)

        except jwt.InvalidTokenError as e:
            #token inválido
            logger.warning(f"Token inválido: {str(e)}")
            raise AuthenticationError("Token inválido", 401)

        except Exception as e:
            logger.error(f"Erro ao gerar token: {str(e)}")
            raise AuthenticationError("Erro ao validar o token", 500)

    def refresh_token(old_token: str) -> str:
        try:
            payload = TokenManager.validate_token(old_token)

            user_id = payload.get("sub")

            # preserva os claims customizados
            custom_claims = {
                k: v for k, v in payload.items()
                if k not in ["sub", "iat", "exp", "jti"]
            }

            new_token = TokenManager.generate_token(user_id, additional_claims=custom_claims)

            logger.info(f"Token renovado para usuário: {user_id}")
            return new_token

        except Exception as e:
            logger.error(f"Erro ao renovar token: {str(e)}")
            raise AuthenticationError("Erro ao renovar token", 401)
