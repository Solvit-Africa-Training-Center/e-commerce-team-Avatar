from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    SellerProfileView,
    UserLocationView,
    UserLoginAPIView,
    UserLogoutAPIView,
    TokenRefreshView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("location/", UserLocationView.as_view(), name="user-location"),
    path("seller-profile/", SellerProfileView.as_view(), name="seller-profile"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
