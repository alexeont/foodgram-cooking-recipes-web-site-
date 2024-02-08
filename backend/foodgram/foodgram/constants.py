# Models:
MAX_NAME_FIELD = 200
TRUNCATED_MODEL_NAME = 10
COLOR_SYMBOLS_COUNT = 7

MIN_COOKING_TIME = 1
MIN_COOKING_TIME_MSG = 'Время приготовления не может равняться нулю'
MAX_COOKING_TIME = 32767
MAX_COOKING_TIME_MSG = 'Больше суток готовится только дипломный проект'

MIN_AMOUNT_FOR_INGREDIENT = 1
MIN_AMOUNT_ERROR_TEXT = 'Количество для ингредиента не может быть меньше 1'
MAX_AMOUNT_FOR_INGREDIENT = 32767
MAX_AMOUNT_ERROR_TEXT = 'Количество для ингредиента не может быть больше 32767'

INVALID_COLOR_FIELD_ERROR_TEXT = 'Цвет не соответствует hex-формату'


# Serializers:
NO_INGREDIENTS_TEXT = 'Добавьте ингредиенты'
NO_TAGS_TEXT = 'Добавьте тэг'
NONEXISTENT_INGREDIENT_TEXT = 'Нет такого ингредиента'
TAGS_DUPLICATE = 'Тэги не должны повторяться'
INGREDIENTS_DUPLICATE = 'Ингредиенты не должны повторяться'

# Views:
NO_RECIPE = {'errors': 'Такого рецепта не существует'}
NONEXISTENT_CART_FAV_ITEM = {'errors': 'Вы не добавляли этого рецепта'}

DOUBLE_SUB = {'errors': 'Вы уже подписаны на этого пользователя'}
SELF_SUB = {'errors': 'Нельзя подписаться на себя'}
NONEXISTENT_SUB = {'errors': 'Вы не подписаны на этого пользователя'}
