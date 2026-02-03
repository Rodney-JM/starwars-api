from typing import Dict, List

class ValidationError(Exception):
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__("Erro(s) de validação: " + errors)