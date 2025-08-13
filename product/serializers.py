# products/serializers.py
from rest_framework import serializers
from .models import (
    Category, Brand, Attribute, AttributeValue,
    Product, ProductImage
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.all(),
        source='attribute',
        write_only=True
    )

    class Meta:
        model = AttributeValue
        fields = ['id', 'value', 'attribute', 'attribute_id']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source='brand',
        write_only=True,
        allow_null=True
    )

    seller = serializers.StringRelatedField(read_only=True)

    attributes = AttributeValueSerializer(many=True, read_only=True)
    attribute_ids = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.all(),
        many=True,
        source='attributes',
        write_only=True
    )

    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description',
            'category', 'category_id',
            'brand', 'brand_id',
            'seller', 'price', 'qty',
            'attributes', 'attribute_ids',
            'images', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)
