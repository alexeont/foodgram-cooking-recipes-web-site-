from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorites,
    ShoppingCart,
    Subscription
)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('get_image',
                    'name',
                    'author',
                    'favorited_count',
                    'ingredient_string')
    search_fields = ('name', 'author', 'tags')
    readonly_fields = ('author', 'favorited_count')
    inlines = (IngredientInline,)

    @admin.display(description='ингредиенты')
    def ingredient_string(self, obj):
        return ', '.join([i.name for i in obj.ingredients.all()])

    @admin.display(description='Добавлен пользовалями в избранное')
    def favorited_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Картинка')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_per_page = 30


@admin.register(Favorites, ShoppingCart)
class FavoritesCartAdmin(admin.ModelAdmin):
    search_fields = ('consumer', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ('subscriber', 'author')
