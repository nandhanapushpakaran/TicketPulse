from rest_framework import permissions
from .models import User

class IsAdminRole(permissions.BasePermission):
    """Allows access only to users with the ADMIN role or superusers."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )


class IsAgentRole(permissions.BasePermission):
    """Allows access only to users with the AGENT role."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.AGENT
        )


class IsAgentOrAdminRole(permissions.BasePermission):
    """Allows access to AGENT or ADMIN users (support staff)."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in (User.Role.AGENT, User.Role.ADMIN) or request.user.is_superuser)
        )


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission allowing owners to access their own objects,
    while support staff (AGENT, ADMIN) have full access.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Support staff can access all objects
        if request.user.role in (User.Role.AGENT, User.Role.ADMIN) or request.user.is_superuser:
            return True

        # Check ownership depending on model fields
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'author'):
            return obj.author == request.user
        if hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False
