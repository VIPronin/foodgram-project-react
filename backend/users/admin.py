from django.contrib import admin

from .models import (
    Follow,
    User
)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'password',
        'email',
        'first_name',
        'last_name',
        # 'role',
        # 'confirmation_code',
    )
    search_fields = (
        'username',
        # 'role',
    )
    list_filter = (
        'email',
        'username',
    )
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        # 'pk',
        'user',
        'following',
    )
    # search_fields = (
    #     'username',
    #     # 'role',
    # )
    list_filter = (
        'user',
        'following',
    )
    empty_value_display = '-пусто-'

admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
