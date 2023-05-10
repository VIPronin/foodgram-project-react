from django.db import models

from users.models import User


class Tag(models.Model):
    """
    Модель тэга к рецепту.
    Привязана к модели Recipe, поэтому стоит выше.
    """
    name = models.CharField(
        verbose_name='Название тега',
        max_length=40,
        unique=True,
        # blank=False
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        default='#49B64E',  # изначально зеленый цвет, отображен в админке
        max_length=7,
        unique=True,
        # blank=False
    )
    slug = models.SlugField(
        verbose_name='slug тега',
        unique=True,
        # blank=False,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингридиента.
    Привязана к модели Recipe, поэтому стоит выше.
    """
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=40
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=40
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=True
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=40
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        help_text='Загрузите сюда картинку вашего рецепта'
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        help_text='Текстовое описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        # through='IngredientRecipe',
        verbose_name='Ингредиенты',
        related_name='recipe_ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """
    Связующая таблица рецепта и ингридиента.
    """
    amount = models.PositiveIntegerField(
        verbose_name='Колличество',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
        related_name='recipe_ingredients',
    )

    class Meta:
        verbose_name = "ингридиента рецепта"
        verbose_name_plural = "ингридиенты рецептов"

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Favorite(models.Model):
    """
    Модель для добавления рецепта в ИЗБРАННОЕ.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites',
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return self.user.username


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"

    def __str__(self):
        return self.user.username
