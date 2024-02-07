from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorites,
                     Tag,
                     Recipe,
                     Ingredient,
                     RecipeIngredient,
                     ShoppingCart,
                     Subscription)
from foodgram.constants import (MAX_AMOUNT_FOR_INGREDIENT,
                                MIN_AMOUNT_FOR_INGREDIENT,
                                NO_INGREDIENTS_TEXT,
                                NO_TAGS_TEXT,
                                TAGS_DUPLICATE,
                                INGREDIENTS_DUPLICATE,
                                DOUBLE_SUB,
                                SELF_SUB,
                                MAX_COOKING_TIME,
                                MIN_COOKING_TIME)
from users.models import User
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """ Ингредиент. """

    class Meta:
        fields = '__all__'
        model = Ingredient


class CustomImageField(Base64ImageField):

    def to_internal_value(self, base64_data):
        if base64_data in self.EMPTY_VALUES:
            self.fail('empty')
        return super().to_internal_value(base64_data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """ Для создания ингредиента в рецепте. """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_AMOUNT_FOR_INGREDIENT,
                                      max_value=MAX_AMOUNT_FOR_INGREDIENT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """ Для отображения ингредиента в рецепте. """

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )

    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('__all__',)


class TagSerializer(serializers.ModelSerializer):
    """ Тег. """

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientGetSerializer(many=True,
                                                source='recipeingredient')
    author = UserSerializer()
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
        read_only_fields = ('__all__',)

    def get_is_favorited(self, obj):
        request = self.context['request']
        return (request and request.user.is_authenticated
                and obj.favorites.filter(consumer=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return (request and request.user.is_authenticated
                and obj.cart_items.filter(consumer=request.user).exists())


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserSerializer(default=serializers.CurrentUserDefault())
    image = CustomImageField(represent_in_base64=True)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME,
                                            max_value=MAX_COOKING_TIME)

    class Meta:
        fields = ('id', 'name', 'author', 'ingredients', 'tags',
                  'image', 'text', 'cooking_time')
        model = Recipe
        read_only_fields = ('author',)

    def validate(self, data):
        ''' Проверка:
            1. Поля ингредиентов и тэгов не пустые
            2. Ингредиенты и тэги не повторяются
            3. Указанные нгредиенты существуют
        '''

        ingredients = data.get('ingredients')

        if not ingredients:
            raise serializers.ValidationError(NO_INGREDIENTS_TEXT)
        if not data.get('tags'):
            raise serializers.ValidationError(NO_TAGS_TEXT)

        ingredients_ids = [ing['ingredient__id'] for ing in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(INGREDIENTS_DUPLICATE)

        if len(data['tags']) != len(set(data['tags'])):
            raise serializers.ValidationError(TAGS_DUPLICATE)
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data.pop('author')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.create_update_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        RecipeIngredient.objects.filter(recipe__id=instance.id).delete()
        self.create_update_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    @staticmethod
    def create_update_ingredients(recipe, ingredients):
        all_ingredients = []
        for ingredient in ingredients:
            all_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('ingredient__id'),
                    amount=ingredient.get('amount')
                )
            )
        RecipeIngredient.objects.bulk_create(all_ingredients)

    def to_representation(self, instance):
        return RecipeGetSerializer(
            context=self.context
        ).to_representation(instance)


class RecipeShortSerializer(RecipeGetSerializer):
    """ Укороченный вывод рецепта для избранного и корзины. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


""" Подписки. """


class SubscriptionGetSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta():
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('__all__',)

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = (self.context['request']
                         .query_params.get('recipes_limit'))
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except TypeError:
                pass
        return RecipeShortSerializer(recipes, many=True).data


class SubscriptionPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('__all__',)

    def validate(self, data):
        author = data['author']

        if author == self.context['request'].user.id:
            raise serializers.ValidationError(SELF_SUB)
        if Subscription.objects.filter(
            author=author,
            subscriber=data['subscriber']
        ).exists():
            raise serializers.ValidationError(DOUBLE_SUB)
        return data

    def to_representation(self, instance):
        return (SubscriptionGetSerializer(context=self.context)
                .to_representation(instance.author))


""" Валидация корзины и избранного. """


class FavCartBaseSerializer(serializers.BaseSerializer):

    def validate(self, attrs):
        if self.Meta.model.objects.filter(
            consumer=attrs['consumer'],
            recipe=attrs['recipe']
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {self.Meta.model._meta.verbose_name}!'
            )
        return attrs

    def to_representation(self, instance):
        return RecipeShortSerializer().to_representation(
            instance.recipe
        )


class FavoritesSerializer(
    FavCartBaseSerializer,
    serializers.ModelSerializer
):
    class Meta:
        model = Favorites
        fields = '__all__'
        read_only_fields = ('__all__',)


class ShoppingCartSerializer(
    FavCartBaseSerializer,
    serializers.ModelSerializer
):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        read_only_fields = ('__all__',)
