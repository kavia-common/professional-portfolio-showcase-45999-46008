from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Allows read-only access for all, write access only for object owners.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None)
        if owner is None and hasattr(obj, "user"):
            owner = getattr(obj, "user")
        return owner == request.user
