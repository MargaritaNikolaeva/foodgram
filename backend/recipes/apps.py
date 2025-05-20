from django.apps import AppConfig


class RecipesConfig(AppConfig):
    verbose_name = 'Рецепты и ингредиенты'
    name = 'recipes'
    default_auto_field = 'django.db.models.BigAutoField'
