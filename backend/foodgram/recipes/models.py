from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (COLOR_SYMBOLS_COUNT,
                                MAX_NAME_AND_SLUG_FIELD,
                                TRUNCATED_MODEL_NAME,
                                MAX_NAME_INGREDIENTS,
                                MIN_AMOUNT_FOR_INGREDIENT,
                                VALIDATE_COOKING_TIME_MSG)

User = get_user_model()


class NameModel(models.Model):
    """ Базовая модель с именем. """

    name = models.CharField(max_length=MAX_NAME_AND_SLUG_FIELD,
                            unique=True,
                            verbose_name='название')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]


class CartFavoritesModel(models.Model):
    """ Базовая модель для корзины и избранного. """
    consumer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class Tag(NameModel):
    """ Тег. """
    color = models.CharField(
        'цвет',
        unique=True,
        max_length=COLOR_SYMBOLS_COUNT
    )
    slug = models.SlugField(
        'слаг',
        max_length=MAX_NAME_AND_SLUG_FIELD,
        unique=True
    )

    class Meta:
        default_related_name = 'tags'
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """ Ингредиент. """
    name = models.CharField('название',
                            max_length=MAX_NAME_AND_SLUG_FIELD)
    measurement_unit = models.CharField('Мера измерения',
                                        max_length=MAX_NAME_INGREDIENTS)

    class Meta:
        default_related_name = 'ingredients'
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]


class Recipe(NameModel):
    """ Рецепт. """
    tags = models.ManyToManyField(Tag, verbose_name='тэги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='ингредиенты',
                                         through='RecipeIngredient',
                                         max_length=MAX_NAME_INGREDIENTS)
    image = models.ImageField(
        'картинка',
        upload_to='recipes/',
    )
    text = models.TextField('текст рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=(MinValueValidator(MIN_AMOUNT_FOR_INGREDIENT,
                                      message=VALIDATE_COOKING_TIME_MSG),)
    )

    class Meta:
        default_related_name = 'recipes_model'
        ordering = ('-id',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class Subscription(models.Model):
    """ Подписка. """
    subscriber = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name='subs_subscriber')
    sub_target = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name='sub_target_subscriber')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'sub_target'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f"{self.subscriber} is a sub of {self.sub_target}"


class ShoppingCart(CartFavoritesModel):
    """ Корзина покупок. """

    class Meta:
        default_related_name = 'cart_items'
        constraints = [
            models.UniqueConstraint(
                fields=['consumer', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return (f"{self.consumer[:TRUNCATED_MODEL_NAME]} добавил "
                f"{self.recipe[:TRUNCATED_MODEL_NAME]} в корзину")


class Favorites(CartFavoritesModel):
    """ Избранное. """

    class Meta:
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['consumer', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return (f"{self.consumer[:TRUNCATED_MODEL_NAME]} добавил "
                f"{self.recipe[:TRUNCATED_MODEL_NAME]} в избранное")


""" Вспомогательные таблицы. """


class RecipeIngredient(models.Model):
    """ Связь рецепта с ингредиентом. """
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='RIngredient',
                                   on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()

    class Meta:
        default_related_name = 'recipeingredient'

    def __str__(self):
        return (f'{self.recipe.name[:TRUNCATED_MODEL_NAME]} '
                f'{self.ingredient.name[:TRUNCATED_MODEL_NAME]}')
