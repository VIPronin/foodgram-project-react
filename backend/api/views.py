from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, IngredientRecipe,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User

from .filters import IngredientFilter
from .pagination import CustomPagination
from .serializers import (CustomUserSerializer, ShortRecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, ShoppingCartSerializer,
                          SubscriptionsSerializer,
                          TagSerializer, UserCreateSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Для отображения рецептов.
    """
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def add_to(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_304_NOT_MODIFIED)

    def delete_from(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        # permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        return self.delete_from(Favorite, request.user, pk)

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
        ingrs = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount'))
        text_list = ['Список необходимых ингредиентов:\n']
        text_list += [
            f'{i.get("ingredient__name").capitalize()} '
            f'({i.get("ingredient__measurement_unit")}) - '
            f'{i.get("sum_amount")}\n' for i in list(ingrs)
        ]
        response = HttpResponse(text_list, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"'
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Для отображения Тэгов.
    Если убрать pagination_class = None  Тэги пропадут с фронта.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Для отображения ингридиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    search_fields = ('^name')


class UsersViewSet(viewsets.ModelViewSet):
    """
    Получить список всех пользователей. Права доступа: Администратор
    """
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    lookup_field = 'pk'

    def get_queryset(self):
        print(self.action)
        if self.action == 'subscriptions':
            subs = self.request.user.following.all()
            return User.objects.filter(follower__in=subs)
        return User.objects.all()

    def get_serializer_class(self):
        print(self.action)
        if self.action in ('list', 'retrieve', 'me'):
            return CustomUserSerializer
        if self.action == 'subscriptions':
            return SubscriptionsSerializer
        return UserCreateSerializer

    @action(['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=False)
    def subscriptions(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, pk):
        user = request.user
        if not User.objects.filter(pk=pk).exists():
            return Response(
                'Объект не найден',
                status=status.HTTP_400_BAD_REQUEST
            )
        author = User.objects.get(pk=pk)
        if request.method == 'POST':
            if user == author:
                return Response(
                    'Нельзя подписаться на себя',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscriptions.objects.filter(
                    following=author,
                    user=user
            ).exists():
                return Response(
                    'Вы уже подписаны',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(following=author, user=user)
            return Response(
                'Подписка успешно создана',
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not Subscriptions.objects.filter(
                    following=author,
                    user=user
            ).exists():
                return Response(
                    'Вы и так не подписаны',
                    status=status.HTTP_400_BAD_REQUEST
                )
            sub = Subscriptions.objects.get(following=author, user=user)
            sub.delete()
        return Response('Успешная отписка', status=status.HTTP_200_OK)
