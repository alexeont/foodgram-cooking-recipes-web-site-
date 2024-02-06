from django_filters import FilterSet, filters

from .models import Recipe


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')

    # Изменил на Boolean, теперь воспринимает только значения True/False,
    # как исправить не нашел. Логичнее всего оставить как было, с ChoiceFilter.

    class Meta:
        model = Recipe
        fields = ('tags',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'author')

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__consumer=user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(cart_items__consumer=user)
        return queryset
