# products/models.py
import os
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify
from PIL import Image

# ---- Image validation config ----
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_FILE_SIZE_MB = 5
MAX_WIDTH = 3000
MAX_HEIGHT = 3000


def validate_image(file):
    # Size check
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Image size cannot exceed {MAX_FILE_SIZE_MB}MB.")
    # Format + dimensions
    try:
        img = Image.open(file)
        fmt = (img.format or "").upper()
        if fmt not in ALLOWED_FORMATS:
            allowed = ", ".join(sorted(ALLOWED_FORMATS))
            raise ValidationError(f"Only {allowed} formats are allowed.")
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            raise ValidationError(
                f"Image dimensions cannot exceed {MAX_WIDTH}x{MAX_HEIGHT}px."
            )
    except Exception:
        raise ValidationError("Invalid image file.")


def product_image_upload_path(instance, filename: str) -> str:
    """
    Store under: products/{productId}-{product-slug}/{original-filename}
    Using id guarantees uniqueness and avoids moves on name changes.
    """
    product = instance.product
    slug = slugify(product.name or "product")
    folder = f"{product.id}-{slug}"  # product.id exists because FK must be set
    return os.path.join("products", folder, filename)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Brand(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Attribute(TimestampedModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class AttributeValue(TimestampedModel):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="values"
    )
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ("attribute", "value")

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(TimestampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField(default=0)
    attributes = models.ManyToManyField(AttributeValue, blank=True, related_name="products")

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
            models.Index(fields=["category"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["seller"]),
        ]

    def __str__(self):
        return self.name

    @property
    def in_stock(self) -> bool:
        return self.qty > 0


class ProductImage(TimestampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=product_image_upload_path, validators=[validate_image])
    name = models.CharField(max_length=255, blank=True)
    alternative_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "id"]
        constraints = [
            # Only one primary image per product
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="uniq_primary_image_per_product",
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name or 'Image'}"
    



class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist")
    created = models.DateTimeField(auto_now_add=True) 

    class Meta:
        unique_together = ["user", "product"]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

