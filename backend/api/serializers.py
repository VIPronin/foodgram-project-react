from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, IngredientRecipe,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиентов. Их может быть много у рецпта.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тэгов. Их может быть много у рецпта.
    """
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вкладки избранное.
    """

    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для карточки покупок.
    """

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для получения данных о пользователях.
    и проверки подписан ли пользователь.
    """
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj: User) -> bool:
        """проверяет подписан ли автор на рецепт"""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.following.filter(user=user).exists()
        )

    class Meta:
        model = User
        fields = '__all__'


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписчиков.
    """

    class Meta:
        model = Subscriptions
        fields = '__all__'


# class ReadIngredientRecipeSerializer(serializers.ModelSerializer):
class ReadIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов и ингридиентов на чтение.
    """
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )
    name = serializers.StringRelatedField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов на чтение.
    """
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_ingredients(self, obj):
        """Возвращает отдельный сериализатор."""
        return ReadIngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return Favorite.objects.filter(
                    user=current_user, recipe=obj.id).exists()
            return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user.is_authenticated:
                return ShoppingCart.objects.filter(
                    user=current_user, recipe=obj.id).exists()
            return False

    # class Meta:
    #     model = Recipe
    #     fields = '__all__'
    #     read_only_fields = '__all__'

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('id', 'slug', 'author', 'created_at', 'updated_at')


class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов и ингридиентов на создание.
    """
    id = serializers.SlugRelatedField(queryset=Ingredient.objects.all(),
                                      slug_field='id')
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов на создание.
    У рецепта может быть много ингридиентов и тэгов.
    Но у ингридиентов и тэгов может быть один рецепт.
    """
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateIngredientRecipeSerializer(
        many=True,
        # write_only=True,
    )

    @staticmethod
    def add_ingredients(recipe, ingredients):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=ingredient.pop('id'),
                recipe=recipe, amount=ingredient.pop('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        self.add_ingredients(recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор мелкий рецпептов на чтение.
    """
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
