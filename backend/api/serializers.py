import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from foodgram_project.constants import MAX_USER_NAME_LENGTH
from recipes.models import (Favorite,
                            Ingredient, IngredientInRecipe,
                            Recipe, ShoppingList)

from users.models import Subscription

User = get_user_model()


class ImageDecode(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserRegistrationSerializer(UserCreateSerializer):
    first_name = serializers.CharField(
        required=True,
        max_length=MAX_USER_NAME_LENGTH
    )

    last_name = serializers.CharField(
        required=True,
        max_length=MAX_USER_NAME_LENGTH
    )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = ImageDecode(required=True)

    class Meta:
        model = User
        fields = ['avatar']


class UserMainSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField(default=None)

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None

    def get_is_subscribed(self, obj):
        req = self.context.get('request')
        return req and req.user.is_authenticated and \
            req.user.subscriptions.filter(subscription=obj).exists()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed',
                  'avatar']


class SubscriptionSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if self.context['request'].user == data.get('subscription'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')

        return data

    def to_representation(self, instance):
        return UserRecipeSerializer(instance.subscription, context=self.context).data

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscription')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['subscriber', 'subscription'],
                message='Подписка уже оформлена.'
            )
        ]


class UserRecipeSerializer(UserMainSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author_recipes.count',
        read_only=True
    )

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        recipes = obj.author_recipes.all()
        if limit:
            recipes = recipes[:int(limit)]

        return RecipeShortSerializer(recipes, many=True).data

    class Meta:
        model = User
        fields = UserMainSerializer.Meta.fields + ['recipes', 'recipes_count']
        read_only_fields = fields.copy()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='ingredients_in_recipe')
    author = UserMainSerializer(read_only=True)
    image = ImageDecode(required=False, allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Не добавлен ни один ингредиент.')
        if len(ingredients) > len({item['id'] for item in ingredients}):
            raise serializers.ValidationError(
                'Ингридиенты не могут повторяться.')

        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated \
            and obj.favorited.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated and \
            obj.shopping_listed.filter(user=request.user).exists()

    def add_ingredients(self, recipe, ingredients_for_recipe):
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients_for_recipe
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe', [])
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        for attr in ['name', 'text', 'image', 'cooking_time']:
            setattr(instance, attr, validated_data.get(
                attr, getattr(instance, attr)))

        instance.save()
        ingredients_data = validated_data.pop('ingredients_in_recipe', [])
        instance.ingredients.clear()
        self.add_ingredients(instance, ingredients_data)
        return instance

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'ingredients', 'image', 'name',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart']
        read_only_fields = ['is_favorited', 'is_in_shopping_cart']


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ListBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', required=False)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = fields.copy()


class FavoriteSerializer(ListBaseSerializer):
    class Meta(ListBaseSerializer.Meta):
        model = Favorite


class ShoppingListSerializer(ListBaseSerializer):
    class Meta(ListBaseSerializer.Meta):
        model = ShoppingList
