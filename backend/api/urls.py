from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    SuSubscriptionCreateDeleteAPIView, 
                    SubscriptionsViewSet, TagViewSet, UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path(
        'docs/',
        TemplateView.as_view(template_name='redoc.html'),
        name='docs'
    ),
    path(
        'users/<int:id>/subscribe/',
        SuSubscriptionCreateDeleteAPIView.as_view(),
        name='subscribe'),
    path(
        'users/subscriptions/',
        SubscriptionsViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
