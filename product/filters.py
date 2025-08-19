# products/filters.py
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "brand", "seller", "attributes", "price_min", "price_max", "in_stock"]

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(qty__gt=0)
        if value is False:
            return queryset.filter(qty__lte=0)
        return queryset
