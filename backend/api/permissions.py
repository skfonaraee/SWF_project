from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Для объектов, связанных с User
        if hasattr(obj, 'user'):
            return obj.user.chat_id == request.user.username
        
        # Для User объектов
        if hasattr(obj, 'chat_id'):
            return obj.chat_id == request.user.username
        
        return False