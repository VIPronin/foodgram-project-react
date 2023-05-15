from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
# from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
# from rest_framework.views import APIView

from recipes.models import (Favorite, Ingredient, Recipe, IngredientRecipe,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User

# from .mixins import ListViewSet
from .filters import IngredientFilter
from .pagination import CustomPagination
# from .permissions import IsAuthorOnly
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
        permission_classes=[IsAuthenticated]
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
        # recipes_in_cart = user.shopping_cart.all()
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
    # queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, )
    # filter_backends = (SearchFilter,)
    # search_fields = ('username',)

    def get_queryset(self):
        print(self.action)
        if self.action == 'subscriptions':
            subs = self.request.user.is_following.all()
            return User.objects.filter(is_followed__in=subs)
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
        print('123345zgdfzgb')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    # def subscribe_post(self, request, pk):
    #     context = {'request': request}
    #     author = get_object_or_404(User, id=pk)
    #     cart_data = {
    #         'user': request.user.id,
    #         'author': author.id
    #     }
    #     serializer = SubscriptionsSerializer(data=cart_data, context=context)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
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
                    author=author,
                    follower=user
            ).exists():
                return Response(
                    'Вы уже подписаны',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(author=author, follower=user)
            return Response(
                'Подписка успешно создана',
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not Subscriptions.objects.filter(
                    author=author,
                    follower=user
            ).exists():
                return Response(
                    'Вы и так не подписаны',
                    status=status.HTTP_400_BAD_REQUEST
                )
            sub = Subscriptions.objects.get(author=author, follower=user)
            sub.delete()
        return Response('Успешная отписка', status=status.HTTP_200_OK)

# class SubscriptionsViewSet(ListViewSet):
#     queryset = Subscriptions.objects.all()
#     serializer_class = SubscriptionsSerializer
#     permission_classes = (IsAuthorOnly, )

#     def get_queryset(self):
#         return Subscriptions.objects.filter(user=self.request.user)


# class SuSubscriptionCreateDeleteAPIView(APIView):
#     permission_classes = (IsAuthenticatedOrReadOnly, )
#     serializer_class = SubscriptionsSerializer

#     @action(methods=('POST', 'DELETE'),
#             url_path='subscribe', detail=True,
#             permission_classes=(IsAuthenticated,))
#     def subscribe_post(self, request, *args, **kwargs):
#         user = request.user
#         following = get_object_or_404(User, pk=self.kwargs.get('user_id'))
#         subscription = Subscriptions.objects.create(
#             user=user, following=following)
#         serializer = SubscriptionsSerializer(
#             subscription,
#             context={'request': request},
#         )
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def subscribe_del(self, request, id):
#         user = request.user
#         following = get_object_or_404(User, id=id)
#         deleted = Subscriptions.objects.get(
#             user=user, following=following).delete()
#         if deleted:
#             return Response({
#                 'message': 'Вы отписались от этого автора'},
#                 status=status.HTTP_204_NO_CONTENT)

    # @action(methods=('POST', 'DELETE'),
    #         url_path='subscribe', detail=True,
    #         permission_classes=(IsAuthenticated,))
    # def subscribe(self, request, pk):
    #     user = request.user
    #     following = get_object_or_404(User, pk=pk)
    #     if request.method == 'POST':
    #         subscription = Subscriptions.objects.create(
    #             user=user, following=following)
    #         serializer = SubscriptionsSerializer(
    #             subscription,
    #             context={'request': request},
    #         )
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     elif request.method == 'DELETE':
    #         following = self.get_object()
    #         deleted = Subscriptions.objects.get(
    #             user=user, following=following).delete()
    #         if deleted:
    #             return Response({
    #                 'message': 'Вы отписались от этого автора'},
    #                 status=status.HTTP_204_NO_CONTENT)

    # def post(self, request, id):
    #     data = {'user': request.user.id, 'author': id}
    #     print(data)
    #     serializer = SubscriptionsSerializer(
    #         data=data,
    #         context={'request': request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data,
    #                     status=status.HTTP_201_CREATED)

    # def delete(self, request, id) -> None:
    #     user = request.user
    #     author = get_object_or_404(User, id=id)
    #     subscription = get_object_or_404(
    #         Subscriptions, user=user, author=author)
    #     if subscription:
    #         subscription.delete()
    #         return Response('Вы отписались от автора.',
    #                         status=status.HTTP_204_NO_CONTENT)
    #     return Response('Вы не подписаны на пользователя',
    #                     status=status.HTTP_400_BAD_REQUEST)
