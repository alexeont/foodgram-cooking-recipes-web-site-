from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return ((obj.author or obj.consumer or obj.subscriber) == request.user
                or request.method in permissions.SAFE_METHODS)

    # Отрабатывает правильно, потому что у Recipe нет consumer и subscriber,
    # а related_name отличается
