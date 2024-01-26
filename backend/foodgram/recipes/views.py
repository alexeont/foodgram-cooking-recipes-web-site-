import io
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
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
from .mixins_views import favorites_cart_mixin, TagIngredientViewMixIn
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipePostSerializer,
                          RecipeGetSerializer)
from foodgram.permissions import IsAuthorOrReadOnly


class TagViewSet(TagIngredientViewMixIn):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(TagIngredientViewMixIn):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipePostSerializer
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == ('list' or 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        return favorites_cart_mixin(self, request, pk, Favorites)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return favorites_cart_mixin(self, request, pk, ShoppingCart)

    @action(detail=False,
            url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart_items__consumer=request.user
        )

        result_dict = {}

        for ingredient in ingredients.values():
            id = ingredient['ingredient_id']
            amount = ingredient['amount']

            if id not in result_dict:
                result_dict[id] = amount
            else:
                result_dict[id] += amount

        to_buy_list = ''
        model_str = '{} ({}) — {}<br/>'

        for id in result_dict:
            ingredient = Ingredient.objects.get(id=id)
            name = ingredient.name.capitalize()
            measure = ingredient.measurement_unit
            to_buy_list += model_str.format(name, measure, result_dict[id])

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
        return FileResponse(buffer,
                            as_attachment=True,
                            filename='список_покупок.pdf')
