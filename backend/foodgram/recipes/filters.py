from django_filters import FilterSet, filters

from .models import Recipe

BOOLEAN_CHOICES = ((0, False),
                   (1, True))


class RecipeFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.ChoiceFilter(choices=BOOLEAN_CHOICES,
                                        method='filter_favorited')
    is_in_shopping_cart = filters.ChoiceFilter(choices=BOOLEAN_CHOICES,
                                               method='filter_shopping_cart')

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if (value == '1') and user.is_authenticated:
            return queryset.filter(favorites__consumer=user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if (value == '1') and user.is_authenticated:
            return queryset.filter(cart_items__consumer=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'author')
