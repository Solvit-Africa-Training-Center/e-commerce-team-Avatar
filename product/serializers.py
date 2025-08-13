from rest_framework import serializers
from .models import Category,Products

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields = '__all__'
    
    
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset = Category.objects.all(), source = 'category', write_only = True
    )
    
    class Meta:
        model = Products
        fields =  ['id', 'name', 'description', 'price', 'stock', 'image', 'created_at', 'category', 'category_id']
        