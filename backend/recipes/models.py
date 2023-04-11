from django.contrib.auth import get_user_model
from django.db import models

from users.models import User
# from backend.users.models import User
# User = get_user_model()


class Tag(models.Model):
    """
    Модель тэга к рецепту.
    Привязана к модели Recipe, поэтому стоит выше.
    """
    name = models.CharField(
        verbose_name='Название тега',
        max_length=40,
        unique=True,
        blank=False
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        # default='#49B64E',
        max_length=7,
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        verbose_name='slug тега',
        unique=True,
        blank=False,
    ) 

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
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )
    measure_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=40
    )

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
        # blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=40
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        # related_name='recipes',
        help_text='Загрузите сюда картинку вашего рецепта'
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        help_text='Текстовое описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes'
    )
    cooking_time =models.DateTimeField(
        verbose_name='Время приготовления в минутах',
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updateed_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


