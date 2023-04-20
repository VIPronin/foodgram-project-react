from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag)
from users.models import (
    Subscriptions,
    User)
from .pagination import CustomPagination
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    CustomUserSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        fav_data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=fav_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def del_from_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        cart_data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(data=cart_data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def del_from_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        filename = f'{user.username}_shopping_list.txt'
        # recipes_in_cart = user.shopping_cart.all()
        ingrs = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measure_unit'
        ).annotate(sum_amount=Sum('amount'))
        text_list = ['Список необходимых ингредиентов:\n']
        text_list += [
            f'{i.get("ingredient__name").capitalize()} '
            f'({i.get("ingredient__measure_unit")}) - '
            f'{i.get("sum_amount")}\n' for i in list(ingrs)
        ]
        response = HttpResponse(text_list, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"'
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class UsersViewSet(viewsets.ModelViewSet):
    """
    Получить список всех пользователей. Права доступа: Администратор
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, )
    lookup_field = 'id'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['post', 'patch', 'get', 'delete']

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=serializer.instance.role)
            return Response(serializer.data)
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        follow_data = {
            'user': request.user.id,
            'author': author.id
        }
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author,
                data=follow_data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data.get('user')
            author = serializer.validated_data.get('author')
            Subscriptions.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(
                Subscriptions,
                user=request.user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        following = request.user.following.all()
        pages = self.paginate_queryset(following)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
