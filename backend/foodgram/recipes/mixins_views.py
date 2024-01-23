from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http.response import Http404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet


from .serializers import RecipeShortSerializer
from foodgram.constants import (DOUBLE_ADD,
                                NO_RECIPE,
                                NONEXISTENT_CART_FAV_ITEM)


def favorites_cart_mixin(self, request, pk, model):
    if request.method == 'POST':
        try:
            model.objects.create(consumer=request.user,
                                 recipe=self.get_object())
            serializer = RecipeShortSerializer(self.get_object())
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(DOUBLE_ADD,
                            status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(NO_RECIPE,
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        self.get_object()
        model.objects.get(
            consumer=request.user,
            recipe__id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response(NONEXISTENT_CART_FAV_ITEM,
                        status=status.HTTP_400_BAD_REQUEST)
    except Http404:
        return Response(NO_RECIPE,
                        status=status.HTTP_404_NOT_FOUND)


class TagIngredientViewMixIn(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (AllowAny,)
