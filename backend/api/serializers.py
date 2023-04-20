from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Ingredient,
    RecipeIngredient,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag)
from users.models import (
    Subscriptions,
    User)

from djoser.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингридиентов. Их может быть много у рецпта.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'
        # fields = (
        #     'id',
        #     'name',
        #     # 'amount',
        #     'measure_unit'
        # )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тэгов. Их может быть много у рецпта.
    """
    class Meta:
        model = Tag
        fields = '__all__'
        # fields = (
        #     'id',
        #     'name',
        #     'color',
        #     'slug'
        # )


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вкладки избранное.
    """

    class Meta:
        model = Favorite
        fields = '__all__'
        # fields = (
        #     'user',
        #     'recipe',
        # )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для карточки покупок.
    """
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        # fields = ('user', 'recipe')


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для получения данных о пользователях.
    """
    class Meta:
        model = User
        fields = '__all__'
        # fields = (
        #     'email',
        #     'id',
        #     'username',
        #     'first_name',
        #     'last_name',
        #     # 'is_subscribed',
        # )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписчиков.
    """
    class Meta:
        model = Subscriptions
        fields = '__all__'
        # fields = (
        #     'email',
        #     'id',
        #     'username',
        #     'first_name',
        #     'last_name',
        #     # 'is_subscribed',
        #     'recipes',
        #     # 'recipes_count',
        # )


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
        # fields = (
        #     'id',
        #     'name',
        #     'author',
        #     'ingredients',
        #     'is_favorited',
        #     'is_in_shopping_cart',
        #     # 'name',
        #     'image',
        #     'text',
        #     # 'cooking_time',
        # )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов и ингридиентов на чтение.
    """
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measure_unit = serializers.StringRelatedField(
        source='ingredient.measure_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = '__all__'
        # fields = (
        #     'amount',
        #     'name',
        #     'measure_unit',
        #     'id'
        # )


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

    def to_representation(self, obj):
        """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
        self.fields.pop('ingredients')
        representation = super().to_representation(obj)
        representation['ingredients'] = RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data
        return representation

    class Meta:
        model = Recipe
        fields = '__all__'
        # fields = (
        #     'id',
        #     'tags',
        #     'author',
        #     'ingredients',
        #     # 'is_favorited',
        #     # 'is_in_shopping_cart',
        #     'name',
        #     'image',
        #     'text',
        #     'cooking_time',
        # )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецпептов на чтение.
    """
    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measure_unit = serializers.StringRelatedField(
        source='ingredient.measure_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = '__all__'
        # fields = (
        #     'amount',
        #     'name',
        #     'measure_unit',
        #     'id'
        # )
