# carts/service.py
from decimal import Decimal
from django.conf import settings
from .models import Cart, CartItem
from .models import Product
from .serializers import ProductSerializer

class CartService:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.session_key = settings.CART_SESSION_ID

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            self.cart_obj = cart
        else:
            self.cart_obj = None
            if self.session_key not in self.session:
                self.session[self.session_key] = {}
            self.cart = self.session[self.session_key]

    def save_session(self):
        self.session.modified = True

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        vendor_id = product.vendor_id
        price = Decimal(product.price)

        if self.request.user.is_authenticated:
            item, created = CartItem.objects.get_or_create(
                cart=self.cart_obj,
                product=product,
                defaults={"price": price, "quantity": quantity, "vendor_id": vendor_id}
            )
            if not created:
                if override_quantity:
                    item.quantity = quantity
                else:
                    item.quantity += quantity
                item.save()
        else:
            if product_id not in self.cart:
                self.cart[product_id] = {
                    "quantity": 0,
                    "price": str(price),
                    "vendor_id": str(vendor_id)
                }
            if override_quantity:
                self.cart[product_id]["quantity"] = quantity
            else:
                self.cart[product_id]["quantity"] += quantity
            self.save_session()

    def remove(self, product):
        product_id = str(product.id)
        if self.request.user.is_authenticated:
            CartItem.objects.filter(cart=self.cart_obj, product=product).delete()
        else:
            if product_id in self.cart:
                del self.cart[product_id]
                self.save_session()

    def __iter__(self):
        if self.request.user.is_authenticated:
            for item in self.cart_obj.items.select_related("product"):
                yield {
                    "product": ProductSerializer(item.product).data,
                    "quantity": item.quantity,
                    "price": item.price,
                    "total_price": item.total_price,
                    "vendor_id": item.vendor_id
                }
        else:
            product_ids = self.cart.keys()
            products = Product.objects.filter(id__in=product_ids)
            cart_copy = self.cart.copy()
            for product in products:
                cart_copy[str(product.id)]["product"] = ProductSerializer(product).data
            for item in cart_copy.values():
                item["price"] = Decimal(item["price"])
                item["total_price"] = item["price"] * item["quantity"]
                yield item

    def __len__(self):
        if self.request.user.is_authenticated:
            return sum(item.quantity for item in self.cart_obj.items.all())
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        if self.request.user.is_authenticated:
            return self.cart_obj.get_total_price()
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self):
        if self.request.user.is_authenticated:
            self.cart_obj.items.all().delete()
        else:
            self.session[self.session_key] = {}
            self.save_session()

    def group_by_vendor(self):
        """
        Returns cart items grouped by vendor for multi-vendor checkout
        """
        vendor_groups = {}
        for item in self:
            vendor_groups.setdefault(item["vendor_id"], []).append(item)
        return vendor_groups

    def sync_session_to_user_cart(self):
        """
        Moves session cart items into the user's DB cart after login
        """
        if not self.request.user.is_authenticated:
            return
        for product_id, data in self.cart.items():
            product = Product.objects.get(id=product_id)
            self.add(product, quantity=data["quantity"], override_quantity=False)
        self.clear()
