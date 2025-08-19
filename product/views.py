# products/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Category, Brand, Attribute, AttributeValue,
    Product, ProductImage
)
from .serializers import (
    CategorySerializer, BrandSerializer, AttributeSerializer, AttributeValueSerializer,
    ProductSerializer, ProductImageSerializer
)
from .filters import ProductFilter
from .permissions import IsSellerOrReadOnly, IsProductSellerOrReadOnly


# --- Reference data viewsets ---
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all().order_by("name")
    serializer_class = AttributeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AttributeValueViewSet(viewsets.ModelViewSet):
    queryset = AttributeValue.objects.select_related("attribute").all().order_by("attribute__name", "value")
    serializer_class = AttributeValueSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# --- Product & Images ---
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProductSellerOrReadOnly]

    def perform_create(self, serializer):
        """
        If you want to create images here, require product in payload.
        The permission check is handled in has_object_permission on updates/deletes.
        For creates, ensure the requester is the product seller.
        """
        product = Product.objects.get(pk=self.request.data.get("product"))
        if product.seller_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the product's seller can add images.")
        serializer.save(product=product)
