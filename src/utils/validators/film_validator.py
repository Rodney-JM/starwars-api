from typing import Dict, List, Any
from validator_manager import Validator

class FilmValidator:
    ALLOWED_FIELDS = [
        'title', 'search', 'director', 'producer',
        'sort_by', 'order', 'page', 'limit', 'fields'
    ]

    ALLOWED_SORTS = [
        'title', 'episode_id', 'release_date', 'director'
    ]

    @classmethod
    def validate(self, params: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}

        field_errors = Validator.validate_query_params(params, self.ALLOWED_FIELDS)
        if field_errors:
            errors.update(field_errors)

        sort_error = Validator.validate_sort_params(
            params.get('sort_by'),
            self.ALLOWED_SORTS
        )
        if sort_error:
            errors['sort_by'] = [sort_error]

        order_error = Validator.validate_order(params.get('order'))
        if order_error:
            errors['order'] = [order_error]

        page_errors = Validator.validate_pagination(
            params.get('page'),
            params.get('limit')
        )
        if page_errors:
            errors.update({k: [v] for k, v in page_errors.items()})

        search_error = Validator.validate_search_query(params.get('search'))
        if search_error:
            errors['search'] = [search_error]

        return errors