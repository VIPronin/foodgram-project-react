# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
# from django.db.models import Avg
# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
# from rest_framework.permissions import (
#     AllowAny,
#     IsAuthenticated,
#     IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    User)

# from .filters import TitleFilter
# from .mixins import GenreCategoryViewSet
# from .permissions import (
#     # AdminModeratorAuthorPermission,
#     # AdminUserOrReadOnly,
#     IsAdmin)
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    CustomUserSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class UsersViewSet(viewsets.ModelViewSet):
    """
    Получить список всех пользователей. Права доступа: Администратор
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (IsAuthenticated)
    # permission_classes = (IsAuthenticated, IsAdmin)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['post', 'patch', 'get', 'delete']

    # @action(
    #     methods=['GET', 'PATCH'],
    #     detail=False,
    #     # permission_classes=(IsAuthenticated,),
    #     url_path='me',
    #     url_name='me'
    # )
    # def info_about_user(self, request):
    #     serializer = CustomUserSerializer(request.user)
    #     if request.method == 'PATCH':
    #         if request.user.is_admin:
    #             serializer = UserSerializer(
    #                 request.user,
    #                 data=request.data,
    #                 partial=True
    #             )

    #         else:
    #             serializer = NotAdminSerializer(
    #                 request.user,
    #                 data=request.data,
    #                 partial=True
    #             )
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# class TitleViewSet(viewsets.ModelViewSet):
#     queryset = Title.objects.all().annotate(
#         Avg("review_title__score")).order_by("name")
#     serializer_class = TitleSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = TitleFilter
#     permission_classes = (AdminUserOrReadOnly,)

#     def get_serializer_class(self):
#         if self.action in ("retrieve", "list"):
#             return ReadOnlyTitleSerializer
#         return TitleSerializer


# class GenreViewSet(GenreCategoryViewSet):
#     """
#     Получение списка  всех  жанров произведений.
#     Права доступа: Доступно без токена
#     """
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer
#     permission_classes = (AdminUserOrReadOnly,)
#     filter_backends = (SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'


# class CategoryViewSet(GenreCategoryViewSet):
#     """
#     Получение всех категорий (типов) произведений.
#     Права доступа: Доступно без токена
#     """
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = (AdminUserOrReadOnly,)
#     filter_backends = (SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'


# class ReviewViewSet(viewsets.ModelViewSet):
#     """
#     Получение отзывов на произведения. Отзыв привязан
#     к определённому произведению.
#     """
#     serializer_class = ReviewSerializer

#     permission_classes = (
#         AdminModeratorAuthorPermission, IsAuthenticatedOrReadOnly
#     )

#     def get_queryset(self):
#         title = get_object_or_404(
#             Title, id=self.kwargs.get('title_id')
#         )
#         return title.review_title.all()

#     def perform_create(self, serializer):
#         title = get_object_or_404(Title, pk=self.kwargs['title_id'])
#         serializer.save(author=self.request.user, title=title)
#         return title.review_title.all()


# class CommentViewSet(viewsets.ModelViewSet):
#     """
#     Получение комментариев к отзывам. Комментарий привязан
#     к определённому отзыву
#     """
#     serializer_class = CommentSerializer
#     permission_classes = (
#         AdminModeratorAuthorPermission, IsAuthenticatedOrReadOnly
#     )

#     def get_queryset(self):
#         review = get_object_or_404(
#             Review,
#             id=self.kwargs.get('review_id'),
#             title=self.kwargs.get('title_id'))
#         return review.comment_review.all()

#     def perform_create(self, serializer):
#         review = get_object_or_404(
#             Review,
#             id=self.kwargs.get('review_id'),
#             title=self.kwargs.get('title_id'))
#         serializer.save(author=self.request.user, review=review)
#         return review.comment_review.all()


