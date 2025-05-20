import hashlib

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram_project.constants import (
    MAX_COOCKING_TIME, MAX_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_NAME_LENGTH, MAX_INGREDIENT_UNIT_LENGTH,
    MAX_RECIPE_NAME_LENGTH, MAX_SHORT_HASH_LENGTH,
    MIN_COOCKING_TIME, MIN_INGREDIENT_AMOUNT)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_INGREDIENT_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_INGREDIENT_UNIT_LENGTH
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_munit',
                violation_error_message='Ингредиент уже существует.'
            )
        ]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe'
    )
    ingredient = models.ForeignKey(
        verbose_name='Ингредиент',
        to=Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во ингредиента',
        default=MIN_INGREDIENT_AMOUNT,
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=f'Кол-во ингредиента должно быть больше {MIN_INGREDIENT_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=f'Кол-во ингредиента должно быть меньше {MAX_INGREDIENT_AMOUNT}'
            )
        )
    )

    def __str__(self):
        return f'Ингредиент в рецепте {self.recipe.name}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('ingredient',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ringredient',
                violation_error_message='Ингредиент уже есть в рецепте.'
            )
        ]


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        to=User,
        on_delete=models.CASCADE,
        related_name='author_recipes'
    )

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_RECIPE_NAME_LENGTH
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/'
    )

    text = models.TextField(
        verbose_name='Описание'
    )

    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты',
        to=Ingredient,
        through=IngredientInRecipe
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                MIN_COOCKING_TIME,
                message=f'Время приготовления должно быть больше {MIN_COOCKING_TIME}'
            ),
            MaxValueValidator(
                MAX_COOCKING_TIME,
                message=f'Время приготовления должно быть меньше {MAX_COOCKING_TIME}'
            )
        )
    )

    short = models.CharField(
        verbose_name='Часть короткой ссылки',
        max_length=MAX_SHORT_HASH_LENGTH,
        blank=True,
        null=True,
        unique=True
    )

    date = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.short:
            unique_string = f'{self.id}-{self.name}-{self.text}'
            hash_object = hashlib.sha256(unique_string.encode())
            self.short = hash_object.hexdigest()[:MAX_SHORT_HASH_LENGTH]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-date',)


class ShoppingList(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_listed'
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shoplist',
                violation_error_message='Рецепт уже добавлен в список покупок.'
            )
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favorited'
    )

    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite',
                violation_error_message='Рецепт уже добавлен в избранное.'
            )
        ]
