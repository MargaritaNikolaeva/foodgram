from django.contrib import admin

from recipes.models import (Favorite,
                            Ingredient, IngredientInRecipe,
                            Recipe, ShoppingList)

admin.site.empty_value_display = 'Не указано'


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited_count')
    search_fields = ('name', 'author__username')
    inlines = [RecipeIngredientInline]

    @admin.display(description='Добавлений в избранное')
    def favorited_count(self, obj):
        return obj.favorited.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_editable = ('ingredient', 'amount')
    search_fields = ('ingredient__name',)
