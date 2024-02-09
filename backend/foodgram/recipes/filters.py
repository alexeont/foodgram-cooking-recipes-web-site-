from django_filters import FilterSet, filters

from .models import Recipe


BOOLEAN_CHOICES = (
    (0, False),
    (1, True)
)


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.ChoiceFilter(choices=BOOLEAN_CHOICES,
                                        method='filter_favorited')
    is_in_shopping_cart = filters.ChoiceFilter(choices=BOOLEAN_CHOICES,
                                               method='filter_shopping_cart')

    # Изменил на Boolean, теперь воспринимает только значения True/False.

    # upd: изменил обратно, потому что без этого фронт
    # не корректно выводил рецепты

    class Meta:
        model = Recipe
        fields = ('tags',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'author')

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if value == '1':
            return queryset.filter(favorites__consumer=user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == '1':
            return queryset.filter(cart_items__consumer=user)
        return queryset
