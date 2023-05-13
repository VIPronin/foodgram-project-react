from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class AdminUserOrReadOnly(permissions.BasePermission):
    """
    Класс прав админ или только для чтения.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class AdminOnly(permissions.BasePermission):
    """
    Класс прав только для администратора.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOnly(permissions.BasePermission):
    """
    Класс прав для работы с избранным и подписками.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False
