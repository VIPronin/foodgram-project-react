from rest_framework import serializers
# from rest_framework.relations import SlugRelatedField
from recipes.models import Tag, Ingredient, Recipe, User
from recipes.models import (
    # Category,
    # Genre, Review,
    # Title,
    Ingredient,
    Recipe,
    Tag,
    User)

from djoser.serializers import UserSerializer

class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиентов. Их может быть много у рецпта.
    """
    class Meta:
        model = Ingredient
        exclude = (
            'id',
            'name',
            'amount',
            'measure_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тэгов. Их может быть много у рецпта.
    """
    class Meta:
        model = Tag
        fields = (
            # 'id',
            'name',
            'color',
            'slug'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов.
    У рецепта может быть много ингридиентов и тэгов.
    Но у ингридиентов и тэгов может быть один рецепт.
    """
    # ingredient = serializers.CharField(
    # #     # slug_field='slug', queryset=Ingredient.objects.all()
    # # )
    # tag = TagSerializer(
    #     # slug_field='slug', queryset=Tag.objects.all()
    # )
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

# class FavoriteSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для вкладки избранное.
#     """


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для карточки покупок.
#     """


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для получения данных о пользователях.
    """
    username = serializers.RegexField(
        required=True, regex=r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', max_length=150
    )


    # def validate(self, data):
    #     if User.objects.filter(username=data.get('username')).exists():
    #         raise serializers.ValidationError('Username занят')
    #     return data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
        )


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписчиков.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
            'recipes',
            # 'recipes_count',
        )



# class CurrentUserDefault(serializers.Serializer):
#     """
#     Сериалайзер для получения дефолтного значения текущего юзера
#     для поля author в ReviewSerializer
#     """
#     requires_context = True

#     def __call__(self, serializer_field):
#         return serializer_field.context['request'].user.username


# class ReviewSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для Review.
#     """
#     author = SlugRelatedField(slug_field='username',
#                               read_only=True, default=CurrentUserDefault)

#     def validate(self, data):
#         title_id = self.context['view'].kwargs.get('title_id')
#         user = self.context['request'].user
#         if self.context['request'].method == 'PATCH':
#             return data
#         is_review_exists = Review.objects.filter(title=title_id,
#                                                  author=user).exists()
#         if is_review_exists:
#             raise serializers.ValidationError('Вы уже оставили отзыв.')
#         return data

#     class Meta:
#         model = Review
#         fields = ('id', 'pub_date', 'author', 'text', 'score')
#         read_only_fields = ('id', 'pub_date', 'author')


# class CommentSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для Комментариев.
#     """
#     author = serializers.SlugRelatedField(
#         slug_field='username', read_only=True
#     )

#     class Meta:
#         model = Comment
#         fields = ('id', 'text', 'author', 'pub_date')
#         read_only_fields = ('id', 'pub_date', 'author')


# class GetTokenSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для получения токенов.
#     """
#     username = serializers.CharField(
#         required=True)
#     confirmation_code = serializers.CharField(
#         required=True)

#     class Meta:
#         model = User
#         fields = (
#             'username',
#             'confirmation_code'
#         )


# class SignUpSerializer(serializers.Serializer):
#     """
#     Сериализатор для авторизации.
#     """
#     username = serializers.RegexField(
#         required=True, regex=r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', max_length=150
#     )
#     email = serializers.EmailField(required=True, max_length=254)

#     def validate(self, data):
#         if data['username'] in ['me', 'ME', 'Me', 'mE']:
#             raise serializers.ValidationError("Недопустимое имя пользователя!")
#         # Делаем данную проверку, т.к. согласно условиям задания пользователь,
#         # созданный администратором должен получить токен, если исключить
#         # данную проверку, падают тесты:
#         # AssertionError: Проверьте, что POST-запрос к /api/v1/auth/signup/ с
#         # данными пользователя, созданного администратором,
#         # возвращает ответ со статусом 200.
#         if User.objects.filter(
#             username=data['username'], email=data['email']
#         ).exists():
#             return data
#         if User.objects.filter(
#             username=data['username']
#         ).exists() or User.objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError(
#                 "Пользователь с такими данными уже существует!"
#             )
#         return data




# class NotAdminSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для неадминистратора.
#     """
#     class Meta:
#         model = User
#         fields = (
#             'username', 'email', 'first_name',
#             'last_name',)
#         read_only_fields = ('role',)


# class TitleSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для создания произведений.
#     """
#     genre = serializers.SlugRelatedField(
#         slug_field='slug', many=True, queryset=Genre.objects.all()
#     )
#     category = serializers.SlugRelatedField(
#         slug_field='slug', queryset=Category.objects.all()
#     )

#     class Meta:
#         fields = '__all__'
#         model = Title


# class ReadOnlyTitleSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор для чтения произведений.
#     """
#     rating = serializers.IntegerField(
#         source='review_title__score__avg', read_only=True
#     )
#     genre = GenreSerializer(many=True)
#     category = CategorySerializer()

#     class Meta:
#         model = Title
#         fields = (
#             'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
#         )
#         read_only_fields = (
#             'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
#         )
