from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductImageViewSet, CategoryViewSet, BrandViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"images", ProductImageViewSet, basename="productimage")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")

urlpatterns = [
    path("", include(router.urls)),
]
