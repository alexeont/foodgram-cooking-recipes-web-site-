from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from recipes.serializers import SubscriptionSerializer
from recipes.models import Subscription


class SubscriptionViewSet(UserViewSet):

    @action(detail=True,
            methods=('post',),
            permission_classes=(IsAuthenticated,),
            url_path='subscribe',)
    def subscribe(self, request, id):
        user = get_object_or_404(User, id=id)

        serializer = SubscriptionSerializer(user)
        serializer.context['request'] = request
        serializer.context['user'] = user
        serializer.validate()
        Subscription.objects.create(subscriber=request.user,
                                    author=user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_sub(self, request, id):
        author = get_object_or_404(User, id=id)
        subscription = request.user.subs_subscriber.filter(
            author=author
        )
        SubscriptionSerializer().validate_deletion(subscription)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=('get',),
            url_path='subscriptions')
    def subscriptions(self, request):
        return (
            self.get_paginated_response(
                SubscriptionSerializer(
                    self.paginate_queryset(
                        User.objects.filter(
                            subs_author__subscriber=self.request.user.id
                        )
                    ),
                    many=True,
                    context={'request': request}
                ).data
            )
        )

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()
