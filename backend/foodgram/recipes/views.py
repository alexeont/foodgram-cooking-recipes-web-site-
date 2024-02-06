import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle

from .models import (Tag,
                     Recipe,
                     Ingredient,
                     ShoppingCart,
                     RecipeIngredient,
                     Favorites)
from .filters import RecipeFilter
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipePostSerializer,
                          RecipeGetSerializer,
                          FavoritesSerializer,
                          ShoppingCartSerializer)
from foodgram.constants import NONEXISTENT_CART_FAV_ITEM, NO_RECIPE
from foodgram.permissions import IsAuthorOrReadOnly


class TagIngredientViewBase(ReadOnlyModelViewSet):
    """ Базовый класс для тэга и ингредиента. """

    pagination_class = None
    permission_classes = (AllowAny,)


class TagViewSet(TagIngredientViewBase):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(TagIngredientViewBase):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipePostSerializer
    queryset = (Recipe.objects.all()
                .select_related('author')
                .prefetch_related('tags', 'ingredients'))
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == ('list' or 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @staticmethod
    def create_favorite_or_cart_object(serializer, model, pk, request):

        data = {
            'recipe': pk,
            'user': request.user.id
        }
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(NO_RECIPE,
                            status=status.HTTP_400_BAD_REQUEST)

        # без try/except не получается отдать 400 ошибку вместо 404.
        # Если объект не получать в сериализаторе, как ты говорил, то
        # его придется получать здесь

        serializer = serializer(data, context={'recipe': recipe})
        serializer.validate(data)

        model.objects.create(consumer=request.user,
                             recipe=recipe)

        return Response(serializer.to_representation(data),
                        status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_favorite_or_cart_object(model, pk, request):

        get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(consumer=request.user,
                                   recipe=pk)
        if not obj.exists():
            return Response(NONEXISTENT_CART_FAV_ITEM,
                            status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def create_pdf(queryset):

        to_buy_list = ''
        model_str = '{} ({}) — {}<br/>'

        for item in queryset:
            ingredient = Ingredient.objects.get(id=item['ingredient_id'])
            name = ingredient.name.capitalize()
            measure = ingredient.measurement_unit
            to_buy_list += model_str.format(name, measure, item['amount'])

        buffer = io.BytesIO()
        file = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
        width, height = A4
        my_style = ParagraphStyle('my_style',
                                  fontName='DejaVuSerif',
                                  fontSize=14)
        file.setFont('DejaVuSerif', 16)
        file.drawString(100, height - 100, 'Список покупок:')

        p1 = Paragraph(to_buy_list, my_style)
        p1.wrapOn(file, 300, 50)
        p1.drawOn(file, width - 450, height - 150)

        file.save()
        buffer.seek(0)
        return buffer

    @action(detail=True,
            methods=('post',),
            url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        return self.create_favorite_or_cart_object(FavoritesSerializer,
                                                   Favorites,
                                                   pk,
                                                   request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_favorite_or_cart_object(Favorites, pk, request)

    @action(detail=True,
            methods=('post',),
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.create_favorite_or_cart_object(ShoppingCartSerializer,
                                                   ShoppingCart,
                                                   pk,
                                                   request)

    @shopping_cart.mapping.delete
    def delete_cart(self, request, pk):
        return self.delete_favorite_or_cart_object(ShoppingCart, pk, request)

    @action(detail=False,
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (RecipeIngredient.objects.filter(
            recipe__cart_items__consumer=request.user
        ).values('ingredient_id')
         .annotate(amount=Sum('amount'))
         .order_by('recipe__name'))
        print(ingredients)

        return FileResponse(self.create_pdf(ingredients),
                            as_attachment=True,
                            filename='список_покупок.pdf')
