from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .serializers import ProductSerializer, CartActionSerializer
from .models import Product
from .service import CartService

@extend_schema(tags=["Cart"])
class CartAPI(APIView):
    """
    API to handle cart operations for guest and logged-in users
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Retrieve current cart",
        description="Returns the cart for the current user (guest or logged in).",
        responses={
            200: OpenApiResponse(
                description="Cart retrieved successfully",
                examples=[
                    OpenApiExample(
                        name="Guest Cart",
                        value={
                            "data": [
                                {"id": 1, "name": "Product A", "quantity": 2, "price": "20.00"}
                            ],
                            "cart_total_price": "40.00",
                            "cart_grouped_by_vendor": {}
                        }
                    ),
                    OpenApiExample(
                        name="Logged-in User Cart",
                        value={
                            "data": [
                                {"id": 2, "name": "Product B", "quantity": 1, "price": "15.00"}
                            ],
                            "cart_total_price": "15.00",
                            "cart_grouped_by_vendor": {}
                        }
                    ),
                ]
            )
        },
       
    )
    def get(self, request, format=None):
        cart = CartService(request)
        return Response(
            {
                "data": list(cart),
                "cart_total_price": cart.get_total_price(),
                "cart_grouped_by_vendor": cart.group_by_vendor()
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Modify cart items",
        description="Add, remove, or clear items in the cart.",
        request=CartActionSerializer,
        responses={202: OpenApiResponse(description="Cart updated successfully")},
        examples=[
            OpenApiExample(
                name="Add Item (Guest or Logged in)",
                value={"action": "add", "product_id": 1, "quantity": 2}
            ),
            OpenApiExample(
                name="Remove Item",
                value={"action": "remove", "product_id": 1}
            ),
            OpenApiExample(
                name="Clear Cart",
                value={"action": "clear"}
            ),
        ]
    )
    def post(self, request, **kwargs):
        serializer = CartActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = CartService(request)
        action = data.get("action")

        if action == "remove":
            product = get_object_or_404(Product, id=data.get("product_id"))
            cart.remove(product)

        elif action == "clear":
            cart.clear()

        elif action == "add":
            product = get_object_or_404(Product, id=data.get("product_id"))
            cart.add(
                product=product,
                quantity=data.get("quantity", 1),
                override_quantity=data.get("override_quantity", False)
            )

        return Response({"message": "Cart updated successfully"}, status=status.HTTP_202_ACCEPTED)