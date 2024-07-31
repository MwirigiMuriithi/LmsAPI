# blogs/permissions.py

from rest_framework.permissions import BasePermission

class IsAuthorOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user is the author of the blog or a superuser
        return obj.author == request.user or request.user.is_superuser
