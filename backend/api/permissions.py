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


# class AdminOnly(permissions.BasePermission):
#     """
#     Класс прав только для администратора.
#     """
#     def has_permission(self, request, view):
#         return (
#             request.user.is_authenticated and request.user.is_admin
#             or request.user.is_staff
#         )

#     def has_object_permission(self, request, view, obj):
#         return (
#             request.user.is_admin
#             or request.user.is_staff
#         )


# class AdminUserOrReadOnly(permissions.BasePermission):
#     """
#     Класс прав админ или только для чтения.
#     """
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         if request.user.is_authenticated:
#             return request.user.is_admin
#         return False

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         if request.user.is_authenticated:
#             return request.user.is_admin
#         return False


# class AdminModeratorAuthorPermission(permissions.BasePermission):
#     """
#     Класс прав только админ или модератор.
#     """
#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_authenticated
#         )

#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or obj.author == request.user
#             or request.user.is_moderator
#             or request.user.is_admin
#         )


# class IsAdmin(permissions.BasePermission):
#     """
#     Класс прав проверка админ/суперюзер.
#     """
#     def has_permission(self, request, view):
#         return (request.user.is_authenticated
#                 and (request.user.is_admin or request.user.is_superuser))
