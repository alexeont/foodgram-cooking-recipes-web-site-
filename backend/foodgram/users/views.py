
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView
from rest_framework.response import Response

from foodgram.constants import (DOUBLE_SUB,
                                SELF_SUB,
                                NONEXISTENT_SUB)
from foodgram.pagination import CustomPaginationForSubs
from recipes.models import Subscription
from recipes.serializers import SubscriptionSerializer

User = get_user_model()


class SubscriptionAPI(CreateAPIView,
                      ListAPIView,
                      DestroyAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPaginationForSubs

    def get_author(self):
        return get_object_or_404(User, id=self.kwargs.get('id'))

    def get_object(self):
        try:
            return Subscription.objects.get(
                sub_target=self.get_author(),
                subscriber=self.request.user
            )
        except Subscription.DoesNotExist:
            return Response(NONEXISTENT_SUB,
                            status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return (User.objects.filter(
                sub_target_subscriber__subscriber=self.request.user))

    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        if user == request.user:
            return JsonResponse(SELF_SUB, status=status.HTTP_400_BAD_REQUEST)

        try:
            Subscription.objects.create(subscriber=request.user,
                                        sub_target=user)
            serializer = self.serializer_class(user)
            recipes_limit = request.query_params.get('recipes_limit', None)
            serializer.context['request'] = request
            return self.get_post_response(
                serializer.data,
                recipes_limit)
        except IntegrityError:
            return JsonResponse(DOUBLE_SUB, status=status.HTTP_400_BAD_REQUEST)

    def get_post_response(self, data, recipes_limit):
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            data["recipes"] = data["recipes"][:recipes_limit]
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        self.get_author()
        instance = self.get_object()
        if not isinstance(instance, Response):
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return instance
