from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscriptions, User


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиентов. Их может быть много у рецпта.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


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


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов на чтение.
    """
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        """Возвращает отдельный сериализатор."""
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов и ингридиентов на чтение.
    """
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = '__all__'


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
    ingredients = RecipeIngredientSerializer()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)

        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(
            create_ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()

            create_ingredients = [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ]
            RecipeIngredient.objects.bulk_create(
                create_ingredients
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
        representation = {}

        for field in self.fields:
            value = field.get_attribute(instance)
            representation[field.field_name] = field.to_representation(value)

        ingredients = RecipeIngredient.objects.filter(recipe=instance)
        representation['ingredients'] = RecipeIngredientSerializer(
            ingredients, many=True
        ).data

        return representation

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов на чтение.
    """
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = '__all__'
