from rest_framework import permissions
from apps.users.models import User

class CanAccessTicket(permissions.BasePermission):
    """
    Ticket access permissions:
    - Staff (AGENT, ADMIN) can access all tickets.
    - Regular USERs can only view or manage their own tickets.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in (User.Role.AGENT, User.Role.ADMIN) or user.is_superuser:
            return True

        return obj.created_by == user


class CanDeleteTicket(permissions.BasePermission):
    """Only Administrators can delete tickets."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == User.Role.ADMIN or user.is_superuser))

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
