from django.contrib.auth.models import AbstractUser
# from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# from .validators import validate_username, validate_year

USER = 'user'
ADMIN = 'admin'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
]


class User(AbstractUser):
    """
    Модель пользователя.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['id', 'username', 'first_name', 'last_name']
    username = models.CharField(
        verbose_name='Логин',
        # validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=150,
        blank=True
    )
    # user_permissions = models.ManyToManyField(
    #     Permission, 
    #     related_name='user_permissions'
    # )
    # role = models.CharField(
    #     verbose_name='роль',
    #     max_length=20,
    #     choices=ROLE_CHOICES,
    #     default=USER
        # blank=True
    # )
    # confirmation_code = models.CharField(
    #     'код подтверждения',
    #     max_length=255,
    #     null=True,
    #     blank=False,
    #     default='XXXX'
    # )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # @property
    # def is_user(self):
    #     """Авторизованный пользователь"""
    #     return self.role == USER

    # @property
    # def is_admin(self):
    #     """Администратор"""
    #     return self.role == ADMIN

    def __str__(self) -> str:
        return self.username