# products/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, AttributeViewSet,
    AttributeValueViewSet, ProductViewSet, ProductImageViewSet, WishlistViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'attributes', AttributeViewSet)
router.register(r'attribute-values', AttributeValueViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'wishlists', WishlistViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
