from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class Validator:
    @staticmethod
    def validate_query_params(params: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, List[str]]:
        errors = {}

        for key in params.keys():
            if key not in allowed_fields:
                if "unknown_fields" not in errors:
                    errors["unknown_fields"] = []
                errors["unknown_fields"].append(
                    f"O campo {key} não é permitido."
                )

        return errors

    @staticmethod
    def validate_sort_params(sort_by: Optional[str], allowed_sorts: List[str]) -> Optional[str]:
        if sort_by and sort_by not in allowed_sorts:
            return f"Ordenação por '{sort_by}' não é permitida. Opções: {', '.join(allowed_sorts) }."
        return None

    @staticmethod
    def validate_order(order: Optional[str]) -> Optional[str]:
        if order and order not in ["asc", "desc"]:
            return "A ordem deve ser 'asc' ou 'desc'"
        return None

    @staticmethod
    def validate_pagination(page: Optional[int], limit: Optional[int]) -> Dict[str, str]:
        #Valida parametros de paginação

        errors = {}
        if page is not None:
            try:
                page_int = int(page)
                if page_int < 1:
                    errors["page"] = "A página deve ser maior que zero."
                if page_int > 1000:
                    errors["page"] = "A página não deve exceder o limite de 1000"
            except (ValueError, TypeError):
                errors["page"] = "O número da página deve ser um numero inteiro."

        if limit is not None:
            try:
                limit_int = int(limit)
                if limit_int < 1:
                    errors["limit"] = "O limite deve ser maior que zero."
                if limit_int > 100:
                    errors["limit"] = "O limite não deve exceder o limite de 100 por página."
            except (ValueError, TypeError):
                errors["limit"] = "O valor do limite deve ser um numero inteiro."

        return errors

    @staticmethod
    def validate_search_query(query: Optional[str]) -> Optional[str]:
        if not query:
            return None

        if len(query) < 2:
            return "A busca deve ter pelo menos 2 caracteres"

        if len(query) > 150:
            return "A busca não deve exceder 150 caracteres"
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r';\s*DROP\s+TABLE',
            r';\s*DELETE\s+FROM',
            r'UNION\s+SELECT',
        ]
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Tentativa de injection detectada: {query}")
                return "Query cotém caracteres ou padrões não permitidos"
        return None

    @staticmethod
    def sanitize_string(value: str, max_length: int = 200) -> str:
        if not value:
            return ""

        sanitized = value.strip()
        sanitized = sanitized[:max_length]
        sanitized = re.sub(r"<[^>]+>", "", sanitized)

        return sanitized