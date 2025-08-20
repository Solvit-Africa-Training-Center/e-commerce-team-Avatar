# products/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Category, Brand, Attribute, AttributeValue,
    Product, ProductImage, Wishlist
)
from .serializers import (
    CategorySerializer, BrandSerializer, AttributeSerializer,
    AttributeValueSerializer, ProductSerializer, ProductImageSerializer, WishlistSerializer
)
from .filters import ProductFilter
from .permissions import IsSellerOrReadOnly
from drf_spectacular.utils import extend_schema

class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects
        .select_related("category", "brand", "seller")
        .prefetch_related("attributes", "images")
        .all()
        .order_by("-created_at")
    )
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_image(self, request, pk=None):
        """
        Optional helper endpoint: POST /products/{id}/add_image/
        body: { image: <file>, name?: str, alternative_text?: str, is_primary?: bool }
        Only the seller can add.
        """
        product = self.get_object()
        if product.seller_id != request.user.id:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        serializer = ProductImageSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            # tie the image to this product
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.select_related("product", "product__seller").all()
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


@extend_schema(tags=["Wishlists"],
             request=WishlistSerializer,
             responses={200: WishlistSerializer(many=True)}
             )
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
