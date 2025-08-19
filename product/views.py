from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, ProductImage, Category, Brand
from .serializers import ProductSerializer, ProductImageSerializer, CategorySerializer, BrandSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Products.
    - Supports filtering by category, brand, seller, and name.
    """
    queryset = Product.objects.all().select_related("category", "brand", "seller")
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "brand", "seller"]
    search_fields = ["name", "description"]


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product Images.
    - Allows CRUD on product images.
    """
    queryset = ProductImage.objects.all().select_related("product")
    serializer_class = ProductImageSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
