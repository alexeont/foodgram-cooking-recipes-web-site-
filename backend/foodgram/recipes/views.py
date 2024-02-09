import io

from django.db.models import Sum
from django.http import FileResponse
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
from foodgram.constants import NONEXISTENT_CART_FAV_ITEM
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
    def create_favorite_or_cart_object(serializer, pk, request):

        data = {
            'recipe': pk,
            'consumer': request.user.id
        }

        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_favorite_or_cart_object(model, pk, request):

        obj = model.objects.filter(consumer=request.user,
                                   recipe=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(NONEXISTENT_CART_FAV_ITEM,
                        status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_pdf(queryset):

        to_buy_list = ''
        model_str = '{} ({}) — {}<br/>'

        for item in queryset:
            name = item['ingredient__name'].capitalize()
            measure = item['ingredient__measurement_unit']
            to_buy_list += model_str.format(name, measure, item['sum_amount'])

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
        return self.create_favorite_or_cart_object(
            FavoritesSerializer,
            pk,
            request
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_favorite_or_cart_object(Favorites, pk, request)

    @action(detail=True,
            methods=('post',),
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.create_favorite_or_cart_object(
            ShoppingCartSerializer,
            pk,
            request
        )

    @shopping_cart.mapping.delete
    def delete_cart(self, request, pk):
        return self.delete_favorite_or_cart_object(ShoppingCart, pk, request)

    @action(detail=False,
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart_items__consumer=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            sum_amount=Sum('amount')
        ).order_by('ingredient__name')

        print(ingredients)

        return FileResponse(self.create_pdf(ingredients),
                            as_attachment=True,
                            filename='список_покупок.pdf')
