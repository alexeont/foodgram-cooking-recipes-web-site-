from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class Admin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return ((obj.author or obj.consumer or obj.subscriber) == request.user
                or request.method in permissions.SAFE_METHODS)


class CustomUserDjoserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.path == '/api/users/me/'
                and not request.user.is_authenticated):
            return False
        return True


class NotInBlackListPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_in_black_list
