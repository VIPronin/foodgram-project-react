from rest_framework import permissions


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
