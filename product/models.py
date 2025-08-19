from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    value = models.CharField(max_length=255)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values")

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    
    # Seller linked to Django's built-in User model
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")

    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()
    attributes = models.ManyToManyField(AttributeValue, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    
    # Optional descriptive name for image
    name = models.CharField(max_length=255, blank=True)
    alternative_text = models.CharField(max_length=255, blank=True)
    
    # ✅ Replaced URLField with ImageField for media uploads
    # - `upload_to="products/"` means images will be saved under MEDIA_ROOT/products/
    # - You can also organize by product ID like "products/%Y/%m/%d/"
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    
    # Keep URL option if you still want remote/external images
    url = models.URLField(blank=True, null=True)

    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.name or 'Image'}"

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
