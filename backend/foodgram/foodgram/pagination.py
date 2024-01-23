from rest_framework.pagination import PageNumberPagination


class CustomLimitPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'


class CustomPaginationForSubs(CustomLimitPagination):
    def get_paginated_response(self, data):
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            for user in data:
                user["recipes"] = user["recipes"][:recipes_limit]
        return super().get_paginated_response(data)
