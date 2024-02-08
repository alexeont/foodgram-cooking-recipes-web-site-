from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import (
    SubscriptionPostSerializer,
    SubscriptionGetSerializer
)
from foodgram.constants import NONEXISTENT_SUB


class SubscriptionViewSet(UserViewSet):

    @action(detail=True,
            methods=('post',),
            permission_classes=(IsAuthenticated,),
            url_path='subscribe',)
    def subscribe(self, request, id):

        data = {
            'subscriber': request.user.id,
            'author': id
        }

        serializer = SubscriptionPostSerializer(data=data)
        serializer.context['request'] = request
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_sub(self, request, id):

        subscription = request.user.subs_subscriber.filter(
            author=id
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(NONEXISTENT_SUB, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=('get',),
            url_path='subscriptions')
    def subscriptions(self, request):
        return (
            self.get_paginated_response(
                SubscriptionGetSerializer(
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
            return (IsAuthenticated(),)
        return super().get_permissions()
