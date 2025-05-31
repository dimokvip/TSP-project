from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS)
        mett = ('GET','HEAD', 'OPTIONS')
        if request.method in mett:
            return True

        # Разрешаем доступ владельцу или администратору
        return obj == request.user or request.user.is_staff


class IsTaskOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        mett = ('GET','HEAD', 'OPTIONS')
        if request.method in mett:
            return True
        return obj.user == request.user or request.user.is_staff


class IsTagOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        mett = ('GET','HEAD', 'OPTIONS')
        if request.method in mett:
            return True
        # Проверяем, что хотя бы одна задача с этим тегом принадлежит пользователю или он админ
        return obj.tasks.filter(user=request.user).exists() or request.user.is_staff
