from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Tag, Ingredient, Recipe, RecipeIngredient


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('get_image', 'name', 'author', 'favorited_count')
    search_fields = ('name', 'author', 'tags')
    readonly_fields = ('author', 'favorited_count')
    inlines = (IngredientInline,)

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
