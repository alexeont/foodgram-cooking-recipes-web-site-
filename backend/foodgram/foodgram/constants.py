# Models:
MAX_NAME_AND_SLUG_FIELD = 200
TRUNCATED_MODEL_NAME = 10
MAX_NAME_INGREDIENTS = 100
VALIDATE_COOKING_TIME_MSG = 'Время приготовления не может равняться нулю'

# Serializers:
MIN_AMOUNT_FOR_INGREDIENT = 1
AMOUNT_ERROR_TEXT = 'Количество для ингредиента не может быть меньше 1.'

COLOR_SYMBOLS_COUNT = 7
INVALID_COLOR_FIELD_ERROR_TEXT = 'Цвет не соответствует hex-формату'
NO_INGREDIENTS_TEXT = 'Добавьте ингредиенты'
NO_TAGS_TEXT = 'Добавьте тэг'
NONEXISTENT_INGREDIENT_TEXT = 'Нет такого ингредиента'
TAGS_DUPLICATE = 'Тэги не должны повторяться'
INGREDIENTS_DUPLICATE = 'Ингредиенты не должны повторяться'

# Views:
DOUBLE_ADD = {'errors': 'Вы уже добавили этот рецепт'}
NO_RECIPE = {'errors': 'Такого рецепта не существует'}
NONEXISTENT_CART_FAV_ITEM = {'errors': 'Вы не добавляли этого рецепта'}

DOUBLE_SUB = {'errors': 'Вы уже подписаны на этого пользователя'}
SELF_SUB = {'errors': 'Нельзя подписаться на себя'}
NONEXISTENT_SUB = {'errors': 'Вы не подписаны на этого пользователя'}
