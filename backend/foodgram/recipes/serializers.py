import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import (Favorites,
                     Tag,
                     Recipe,
                     Ingredient,
                     RecipeIngredient,
                     ShoppingCart)
from .mixins_serializers import favorites_cart_check
from foodgram.constants import (AMOUNT_ERROR_TEXT,
                                INVALID_COLOR_FIELD_ERROR_TEXT,
                                MIN_AMOUNT_FOR_INGREDIENT,
                                NO_INGREDIENTS_TEXT,
                                NO_TAGS_TEXT,
                                NONEXISTENT_INGREDIENT_TEXT,
                                TAGS_DUPLICATE,
                                INGREDIENTS_DUPLICATE)
from users.serializers import CustomUserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """ Обработка поля картинки. """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """ Ингредиент. """

    class Meta:
        fields = '__all__'
        model = Ingredient


class IdSerializerField(serializers.IntegerField):
    """ Для замены поля id в ингредиенте для создания рецепта. """
    def to_representation(self, value):
        value = value.id
        return super().to_representation(value)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """ Для создания ингредиента в рецепте. """
    id = IdSerializerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if (value < MIN_AMOUNT_FOR_INGREDIENT):
            raise serializers.ValidationError(AMOUNT_ERROR_TEXT)
        return value


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """ Для отображения ингредиента в рецепте. """
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('__all__',)

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class TagSerializer(serializers.ModelSerializer):
    """ Тег. """

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientGetSerializer(many=True,
                                                source='recipeingredient')
    author = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField(source='image')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        model = Recipe

    def get_image(self, obj):
        return obj.image.url

    def get_author(self, obj):
        return CustomUserSerializer(obj.author, context=self.context).data

    def get_is_favorited(self, obj):
        return favorites_cart_check(self, obj, Favorites)

    def get_is_in_shopping_cart(self, obj):
        return favorites_cart_check(self, obj, ShoppingCart)


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient',
                                             required=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all(),
                                              required=True)
    author = serializers.CharField(default=serializers.CurrentUserDefault())
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'name', 'author', 'ingredients', 'tags',
                  'image', 'text', 'cooking_time')
        model = Recipe
        read_only_fields = ('author',)

    def validate_color(value):
        if (len(value) != 7 or value[0] != '#'):
            raise serializers.ValidationError(INVALID_COLOR_FIELD_ERROR_TEXT)
        return value

    def validate(self, data):
        ''' Проверка:
            1. Поля ингредиентов и тэгов не пустые
            2. Ингредиенты и тэги не повторяются
            3. Указанные нгредиенты существуют
        '''

        super().validate(data)

        ingredients = data.get('recipeingredient')

        if not ingredients:
            raise serializers.ValidationError(NO_INGREDIENTS_TEXT)
        if not data.get('tags'):
            raise serializers.ValidationError(NO_TAGS_TEXT)

        ingredients_ids = [ing['ingredient'] for ing in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(INGREDIENTS_DUPLICATE)

        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(TAGS_DUPLICATE)

        for ingredient in ingredients:
            try:
                id = ingredient["ingredient"]
                Ingredient.objects.get(id=id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'{NONEXISTENT_INGREDIENT_TEXT}: {id}'
                )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('ingredient')
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        RecipeIngredient.objects.filter(recipe__id=instance.id).delete()
        recipe = Recipe.objects.get(id=instance.id)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('ingredient')
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )
        instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            context=self.context
        ).to_representation(instance)


class RecipeShortSerializer(RecipeGetSerializer):
    """ Укороченный вывод рецепта. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


""" Подписки. """


class SubscriptionSerializer(CustomUserSerializer):
    recipes = RecipeShortSerializer(many=True, source='recipes_model')
    recipes_count = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('__all__',)
        extra_kwargs = {
            'email': {'validators': []},
            'username': {'validators': []}

        }

    def get_recipes_count(self, obj):
        return obj.recipes_model.count()
