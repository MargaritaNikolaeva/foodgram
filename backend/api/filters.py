from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class CustomSearchFilter(SearchFilter):
    search_param = 'name'

    def get_search_terms(self, request):
        search = super().get_search_terms(request)
        return [item.lower() for item in search]


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author', lookup_expr='exact')
    is_favorited = filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_in_shopping_cart')

    def filter_in_shopping_cart(self, queryset, name, is_in_shopping_cart):
        user = self.request.user
        if user.is_authenticated and is_in_shopping_cart == 1:
            return queryset.filter(shopping_listed__user=user)
        return queryset

    def filter_favorited(self, queryset, name, is_favorited):
        user = self.request.user
        if user.is_authenticated and is_favorited == 1:
            return queryset.filter(favorited__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart')
