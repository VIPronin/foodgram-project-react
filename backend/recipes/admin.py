from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )
    # list_editable = ('group',)
    list_filter = (
        'author',
        'name',
        'tags',
        )
    # search_fields = ('pub_date',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


class RecipeIngredient(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient'
    )
    # list_editable = ('group',)
    list_filter = (
        'recipe',
        'ingredient'
        )
    # search_fields = ('pub_date',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'

class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measure_unit'
    )
    list_filter = (
        'name',
        )
    empty_value_display = '-пусто-'

class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = (
        'user',
        'recipe'
        )
    empty_value_display = '-пусто-'

class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = (
        'user',
        'recipe'
        )
    empty_value_display = '-пусто-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
