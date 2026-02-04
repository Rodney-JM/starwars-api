from config import Config
from typing import Optional, Dict, Any, List
import time
import logging
import requests
from ...utils.cache import get_from_cache, set_in_cache
from .exceptions import SWAPIError, SWAPIConnectionError, SWAPINotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwapiManager:
    def __init__(self):
        self.base_url = Config.SWAPI_BASE_URL
        self.timeout = Config.SWAPI_TIMEOUT
        self.max_retries = Config.SWAPI_MAX_RETRIES

    #buscando os dados
    def fetch(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        cache_key = self._build_cache_key(endpoint, params)

        cached = get_from_cache(cache_key)
        if cached is not None:
            logger.info(f"Cache HIT: {endpoint}")
            return cached

        # cache -> miss entao faz a chamada http
        url = f"{self.base_url}/{endpoint}/"
        data = self._http_get_with_retry(url, params)

        set_in_cache(cache_key, data)
        logger.info(f"Dados salvos no cache: {endpoint}")

        return data

    def fetch_by_id(self, endpoint: str, resource_id: int) -> Dict[str, Any]:
        return self.fetch(f"{endpoint}/{resource_id}")

    def fetch_all(self, endpoint: str) -> List[Dict[str, Any]]:
        cache_key = f"all_{endpoint}"
        cached = get_from_cache(cache_key)
        if cached is not None:
            logger.info(f"Todos os dados de '{endpoint}' retornados do cache")
            return cached

        all_results: List[Dict[str, Any]] = []
        #começando pela url da primeira pagina
        next_url: Optional[str] = f"{self.base_url}/{endpoint}/"

        while next_url:
            data = self._http_get_with_retry(next_url)
            all_results.extend(data.get("results"), [])

            next_url = data.get("next")
            logger.debug(f"Página coletada. Total até agora: {len(all_results)}")
        #salvamento no cache
        set_in_cache(cache_key, all_results)
        logger.info(f"Total de {len(all_results)} itens coletados de '{endpoint}'")
        return all_results

    def fetch_by_url(self, url: str) -> Dict[str, Any]:
        cache_key = f"url_{url}"
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached

        data = self._http_get_with_retry(url)
        set_in_cache(cache_key, data)
        return data

    def _http_get_with_retry(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        # faz o GET com retry automático e backoff exponencial
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[Tentativa {attempt}/{self.max_retries}] GET {url}")
                response = requests.get(url, params=params, timeout=self.timeout)
                if response.status_code == 404:
                    raise SWAPINotFoundError(url, "desconhecido")

                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na tentativa: {attempt}")
                if attempt == self.max_retries:
                    raise SWAPIConnectionError()
                #Backoff exponencial
                wait_time = 2** (attempt -1)
                logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
            except requests.exceptions.ConnectionError:
                logger.warning(f"Erro de conexão na tentativa {attempt}")
                if attempt == self.max_retries:
                    raise SWAPIConnectionError()
                wait_time = 2** (attempt -1)
                time.sleep(wait_time)
            except SWAPINotFoundError:
                raise

            except requests.exceptions.HTTPError as e:
                logger.error(f"Erro HTTP: {e}")
                raise SWAPIError(f"Erro na SWAPI: {str(e)}", getattr(e.response, "status_code", 500))

            raise SWAPIConnectionError()


    @staticmethod
    def _build_cache_key(endpoint: str, params: Optional[Dict] = None) -> str:
        key = f"swapi:{endpoint}"
        if params:
            sorted_params = sorted(params.items())
            key += ":" + ":".join(f"{k}={v}" for k, v in sorted_params if v)
        return key