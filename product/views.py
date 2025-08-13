from django.shortcuts import render
from .models import Category, Products
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import viewsets, filters

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all().order_by('created_at')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    filter_fields = ['category', 'price']