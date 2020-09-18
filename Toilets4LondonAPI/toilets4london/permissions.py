from rest_framework import permissions


# https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/#authenticating-with-the-api


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user or request.user.is_staff


class IsReviewerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow reviewers of a toilet or staff to see the review
    Anyone who is authenticated can post a review
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return permissions.IsAuthenticated
        else:
            return obj.user == request.user or request.user.is_admin


class IsAdminUserOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin

