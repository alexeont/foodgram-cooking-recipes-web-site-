from django.contrib import admin

from .models import Tag, Ingredient, Recipe, Favorites


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author', 'tags')
    readonly_fields = ('author', 'favorited_count')

    @admin.display(description='Добавлен пользовалями в избранное')
    def favorited_count(self, obj):
        return Favorites.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_per_page = 30
