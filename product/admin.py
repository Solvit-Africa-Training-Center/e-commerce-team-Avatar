from django.contrib import admin
from .models import Category, Product, Brand, Attribute, AttributeValue, ProductImage
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(ProductImage)