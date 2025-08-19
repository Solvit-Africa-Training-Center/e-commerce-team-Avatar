from rest_framework import serializers
from .models import Product, ProductImage, Category, Brand


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for handling product images.
    - Returns absolute URL for easy frontend integration.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "name", "alternative_text", "image", "image_url", "is_primary"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Products.
    - Includes nested images.
    """
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "seller", "category", "brand", "name", "slug",
            "description", "price", "created_at", "updated_at", "images"
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug"]
