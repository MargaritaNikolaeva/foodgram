from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram_project.constants import MAX_EMAIL_LENGTH, MAX_USER_NAME_LENGTH


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        error_messages={
            'unique': 'Адрес электронной почты уже используется.'
        }
    )

    username = models.CharField(
        verbose_name='Уникальное имя пользователя',
        max_length=MAX_USER_NAME_LENGTH,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=f'Имя пользователя содержит запрещенные символы.'
                        f'Оно может содержать только буквы, цифры и символы @/./+/-/_'
            ),
        ),
        error_messages={
            'unique': 'Имя пользователя уже используется.'
        }
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_USER_NAME_LENGTH
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_USER_NAME_LENGTH
    )

    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/avatars/',
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        verbose_name='Подписчик',
        to=FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    subscription = models.ForeignKey(
        verbose_name='Подписка',
        to=FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    def __str__(self):
        return f'{self.subscriber.username} подписан на {self.subscription.username}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscription'],
                name='unique_sub',
                violation_error_message='Подписка уже оформлена.'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscription')),
                name='no_self_subscribed'
            )
        ]
