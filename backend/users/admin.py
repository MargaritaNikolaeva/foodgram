from django.contrib import admin

from users.models import FoodgramUser, Subscription

admin.site.empty_value_display = 'Не указано'


@admin.register(FoodgramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name',
                    'last_name', 'email', 'is_staff',
                    'subscribers_count', 'recipes_count')
    search_fields = ('email', 'username')

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribers.count()

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.author_recipes.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscription')
    search_fields = ('subscriber', )
