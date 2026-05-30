from rest_framework.permissions import BasePermission


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user or
            request.user in obj.members.all()
        )