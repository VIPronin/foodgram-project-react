from django_filters.rest_framework import FilterSet, filters
from django.db.models import Q
from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    name = filters.CharFilter(method='filter_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(Q(name__istartswith=value))
