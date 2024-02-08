from rest_framework import serializers

from .models import User
from foodgram.constants import DOUBLE_SUB, SELF_SUB
from recipes.models import Subscription


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (request and request.user.is_authenticated
                and obj.subs_author.filter(subscriber=request.user).exists())


""" Подписки. """


class SubscriptionGetSerializer(UserSerializer):

    from recipes.serializers import RecipeShortSerializer

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
        return self.RecipeShortSerializer(recipes, many=True).data


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
        return SubscriptionGetSerializer(
            context=self.context
        ).to_representation(instance.author)
