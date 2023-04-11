from django.urls import include, path
from rest_framework.routers import SimpleRouter
# from rest_framework.routers import SimpleRouter

from .views import (
    APIGetToken,
    APISignup,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    # CategoryViewSet,
    # CommentViewSet,
    # GenreViewSet,
    # ReviewViewSet,
    # TitleViewSet,
    UsersViewSet)

router_v1 = SimpleRouter()
router_v1.register('recipes', RecipeViewSet)
router_v1.register('users', UsersViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)

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
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
]