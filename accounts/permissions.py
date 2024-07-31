# accounts/permissions.py

from rest_framework.permissions import BasePermission

class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.is_active
