from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AvatarAPIView,
                       FoodgramUserViewSet, IngredientViewSet,
                       RecipeViewSet)


router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', FoodgramUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', FoodgramUserViewSet.as_view({'get': 'me'})),
    path('users/set_password/', FoodgramUserViewSet.as_view({'post': 'set_password'}),
         name='set_password'),
    path('users/me/avatar/', AvatarAPIView.as_view(), name='avatar'),
    path('auth/', include('djoser.urls.authtoken'))
]
