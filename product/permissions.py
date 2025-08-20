# products/permissions.py
from rest_framework import permissions

class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Read for everyone.
    Write only for the product's seller.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # obj is Product
        return getattr(obj, "seller_id", None) == getattr(request.user, "id", None)


class IsProductSellerOrReadOnly(permissions.BasePermission):
    """
    For ProductImage operations: only the product's seller can modify.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # obj is ProductImage
        return getattr(obj.product, "seller_id", None) == getattr(request.user, "id", None)
