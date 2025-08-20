# products/serializers.py
from rest_framework import serializers
from .models import (
    Category, Brand, Attribute, AttributeValue,
    Product, ProductImage
)

# --- Simple serializers ---
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "created_at", "updated_at"]


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ["id", "name", "created_at", "updated_at"]


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.all(),
        source="attribute",
        write_only=True
    )

    class Meta:
        model = AttributeValue
        fields = ["id", "value", "attribute", "attribute_id", "created_at", "updated_at"]


# --- Product Image ---
class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            "id", "product", "image", "image_url",
            "name", "alternative_text", "is_primary",
            "created_at", "updated_at"
        ]
        read_only_fields = ["product"]  # product set via URL or overridden in view if needed

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# --- Product ---
class ProductSerializer(serializers.ModelSerializer):
    # Read-only nested objects
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    attributes = AttributeValueSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    # Write-only foreign keys
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(), source="brand", write_only=True, allow_null=True, required=False
    )
    attribute_ids = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.all(), many=True, source="attributes", write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "description",
            "category", "category_id",
            "brand", "brand_id",
            "seller", "price", "qty", "in_stock",
            "attributes", "attribute_ids",
            "images", "created_at", "updated_at"
        ]
        read_only_fields = ["seller", "in_stock", "created_at", "updated_at"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_qty(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def create(self, validated_data):
        # attach seller from request
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["seller"] = request.user
        return super().create(validated_data)
