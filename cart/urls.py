from django.urls import path
from .views import CartAPI

urlpatterns = [
    
    
    path('cart', CartAPI.as_view(), name='cart'),

]