from django.urls import include, path
from rest_framework.routers import DefaultRouter
# from rest_framework.routers import SimpleRouter

from .views import (
    # APIGetToken,
    # APISignup,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'users', UsersViewSet)
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingredients', IngredientViewSet)

# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )

urlpatterns = [
    # path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
    # path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]