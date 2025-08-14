from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class CartActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["add", "remove", "clear"])
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False, min_value=1, default=1)
    override_quantity = serializers.BooleanField(required=False, default=False)