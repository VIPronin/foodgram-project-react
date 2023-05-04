from django_filters.rest_framework import FilterSet, filters
# from django.db.models import Q
from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
