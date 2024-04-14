from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение автором объекта, для всех остальных только чтение."""

    message = 'Досутпно авторам объектов или только для чтение'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            and obj.author == request.user
        )


class IsShopOnly(BasePermission):
    """Разрешение только магазинам."""

    message = 'Доступно только для магазинов'

    def has_permission(self, request, view):
        return request.user.type == 'shop'