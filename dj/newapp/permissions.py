from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """
    Разрешает доступ только владельцу объекта или администратору.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Разрешаем доступ владельцу или администратору
        return obj == request.user or request.user.is_staff


class IsTaskOwnerOrAdmin(BasePermission):
    """
    Разрешает доступ к задаче только её владельцу или администратору.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class IsTagOwnerOrAdmin(BasePermission):
    """
    Разрешает доступ к тегу только владельцу связанной задачи или администратору.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Проверяем, что хотя бы одна задача с этим тегом принадлежит пользователю или он админ
        return obj.tasks.filter(user=request.user).exists() or request.user.is_staff
