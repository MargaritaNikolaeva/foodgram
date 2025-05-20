from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.urls import include, path
from recipes.models import Recipe


def short_redirect(request, short_path):
    recipe = get_object_or_404(Recipe, short=short_path)
    url = request.build_absolute_uri(f'/recipes/{recipe.id}/')
    return redirect(url)


urlpatterns = [
    path('api/', include('api.urls')),
    path('s/<str:short_path>/', short_redirect),
    path('admin/', admin.site.urls)
]
