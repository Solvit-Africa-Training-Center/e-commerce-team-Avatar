from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from drf_spectacular.utils import extend_schema

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

@extend_schema(tags=["Categories"])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@extend_schema(tags=["Brands"])
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Attributes"])
class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Attribute Values"])
class AttributeValueViewSet(viewsets.ModelViewSet):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category', 'brand', 'seller').prefetch_related('attributes', 'images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    filterset_fields = ['category', 'brand', 'seller', 'attributes']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

@extend_schema(tags=["Product Images"])
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.AllowAny]
