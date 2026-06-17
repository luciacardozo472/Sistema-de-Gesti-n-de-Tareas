from rest_framework.permissions import BasePermission


class IsAdminLevel(BasePermission):
    message = 'Solo el administrador puede realizar esta acción.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.level == 0
        )