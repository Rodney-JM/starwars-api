import sys
import os
import time
import logging
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from typing import List, Any, Dict, Optional
from config import Config
from ...utils.cache import get_from_cache, set_in_cache


class SWAPIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Recurso não encontrado
class SWAPINotFoundError(SWAPIError):
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(f"{resource} com ID ' {resource_id} ' não encontrado", 404)

# Erro de conexao
class SWAPIConnectionError(SWAPIError):
    def __init__(self):
        super().__init__(
            "Não foi possível conectar ao SWAPI. tente novamente mais tarde", 503
        )

