from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_color
from foodgram.constants import (
    MAX_NAME_FIELD,
    TRUNCATED_MODEL_NAME,
    MIN_COOKING_TIME,
    MIN_COOKING_TIME_MSG,
    MAX_COOKING_TIME,
    MAX_COOKING_TIME_MSG,
    MIN_AMOUNT_FOR_INGREDIENT,
    MIN_AMOUNT_ERROR_TEXT,
    MAX_AMOUNT_FOR_INGREDIENT,
    MAX_AMOUNT_ERROR_TEXT,
    COLOR_SYMBOLS_COUNT,
)
from users.models import User


class NameModel(models.Model):
    """ Базовая модель с именем. """

    name = models.CharField(max_length=MAX_NAME_FIELD,
                            verbose_name='название')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:TRUNCATED_MODEL_NAME]


class CartFavoritesModel(models.Model):
    """ Базовая модель для корзины и избранного. """

    consumer = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('consumer', 'recipe'),
                name='%(class)s prevent double add'
            ),
        )

    def __str__(self):
        return (f'{self.consumer} добавил рецепт {self.recipe.name}'
                f'в {self._meta.verbose_name}')


class Tag(NameModel):
    """ Тег. """

    color = models.CharField(
        'цвет',
        unique=True,
        validators=(validate_color,),
        max_length=COLOR_SYMBOLS_COUNT
    )
    slug = models.SlugField(
        'слаг',
        max_length=MAX_NAME_FIELD,
        unique=True
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(NameModel):
    """ Ингредиент. """

    measurement_unit = models.CharField('Мера измерения',
                                        max_length=MAX_NAME_FIELD)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_measure'
            ),
        )

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
                                         through='RecipeIngredient')
    image = models.ImageField(
        'картинка',
        upload_to='recipes/'
    )
    text = models.TextField('текст рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message=MIN_COOKING_TIME_MSG
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=MAX_COOKING_TIME_MSG
            )
        )
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        default_related_name = 'recipes'
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class Subscription(models.Model):
    """ Подписка. """

    subscriber = models.ForeignKey(User,
                                   verbose_name='подписчик',
                                   on_delete=models.CASCADE,
                                   related_name='subs_subscriber')
    author = models.ForeignKey(User,
                               verbose_name='автор',
                               on_delete=models.CASCADE,
                               related_name='subs_author')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('subscriber', 'author'),
                name='unique_subscription'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(subscriber=models.F('author')),
            ),
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.subscriber.get_full_name()} подписан на '
                f'{self.author.get_full_name()}')


class ShoppingCart(CartFavoritesModel):
    """ Корзина покупок. """

    class Meta(CartFavoritesModel.Meta):
        default_related_name = 'cart_items'
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'


class Favorites(CartFavoritesModel):
    """ Избранное. """

    class Meta(CartFavoritesModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'


""" Вспомогательные таблицы. """


class RecipeIngredient(models.Model):
    """ Связь рецепта с ингредиентом. """

    recipe = models.ForeignKey(Recipe,
                               verbose_name='рецепт',
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name='ингредиент',
                                   on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'количество',
        validators=(
            MinValueValidator(
                MIN_AMOUNT_FOR_INGREDIENT,
                message=MIN_AMOUNT_ERROR_TEXT
            ),
            MaxValueValidator(
                MAX_AMOUNT_FOR_INGREDIENT,
                message=MAX_AMOUNT_ERROR_TEXT
            )
        )
    )

    class Meta:
        default_related_name = 'recipeingredient'
        verbose_name = 'рецепт и ингредиент'
        verbose_name_plural = 'рецепты и ингредиенты'

    def __str__(self):
        return (f'{self.recipe.name[:TRUNCATED_MODEL_NAME]} '
                f'{self.ingredient.name[:TRUNCATED_MODEL_NAME]}')
