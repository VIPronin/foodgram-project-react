from django.contrib import admin

from .models import (
    Subscriptions,
    User
)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'password',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
    )
    list_filter = (
        'email',
        'username',
    )
    empty_value_display = '-пусто-'


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    list_filter = (
        'user',
        'following',
    )
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
