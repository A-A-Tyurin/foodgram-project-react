''' Views for 'recipes' API application. '''

from django.db.models import Sum
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, permissions, status, validators,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import AuthorOrAdmin
from recipes.models import Ingredient, Recipe, Tag
from .filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, TagSerializer)


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    ''' ViewSet for tag actions. '''
    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    ''' ViewSet for ingredient actions. '''
    http_method_names = ['get']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    ''' ViewSet for recipe actions. '''
    http_method_names = ['get', 'post', 'put', 'delete']
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        '''
        Instantiates and returns the list of permissions
        that this view requires.
        '''
        if self.action in ['list', 'retrieve']:
            permission_classes = (permissions.AllowAny,)
        if self.action in ['update', 'destroy']:
            permission_classes = (AuthorOrAdmin,)
        return [permission() for permission in permission_classes]

    def _set_recipe_to_related(self, related_manager):
        ''' Process common recipe actions. '''
        recipe = self.get_object()
        if self.request.method == 'DELETE':
            related_manager.get(recipe_id=recipe.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if related_manager.filter(recipe=recipe).exists():
            raise validators.ValidationError(
                _('The recipe already exists.')
            )
        related_manager.create(recipe=recipe)
        serializer = RecipeShortSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'delete'], name='favorite')
    def favorite(self, request, pk=None):
        ''' Process user favorite recipe actions. '''
        return self._set_recipe_to_related(
            request.user.favorite_recipes
        )

    @action(detail=True, methods=['get', 'delete'],
            name='shopping_cart')
    def shopping_cart(self, request, pk=None):
        ''' Process user shopping cart actions. '''
        return self._set_recipe_to_related(
            request.user.shopping_cart
        )

    @action(detail=False, methods=['get'],
            name='download_shopping_cart')
    def download_shopping_cart(self, request, pk=None):
        ''' Get a file with a list of ingredients from shopping cart. '''
        data = (
            request.user.shopping_cart
                   .values_list(
                        'recipe__ingredients__ingredient__name',
                        'recipe__ingredients__ingredient__measurement_unit',
                   ).annotate(summary=Sum('recipe__ingredients__amount'))
        )
        items = (
            ['{} {}{}'.format(item[0], item[2], item[1]) for item in data]
        )
        response = HttpResponse(
            '\n'.join(items), content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = ('attachment;'
                                           ' filename="shopping_cart.txt"')
        return response