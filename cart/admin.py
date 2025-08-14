from django.contrib import admin

from .models import Cart

# Register your models here.

admin.site.site_header = "E-Commerce Admin"
admin.site.register(Cart)