from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login

from .models import User, SellerProfile, Location
from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    UserProfileSerializer,
    SellerProfileSerializer,
    LocationSerializer
)
from .utils import send_otp_email, verify_otp

# -------------------------------
# User Registration View
# -------------------------------
@extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={201: dict, 400: dict}
)
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # user + location created automatically

            # Automatically create SellerProfile if user is a seller
            if user.role == 'seller':
                SellerProfile.objects.get_or_create(
                    user=user,
                    defaults={'store_name': f"{user.full_name}'s Store"}
                )

            send_otp_email(user)  # send OTP to email
            return Response(
                {'message': 'User registered successfully. OTP sent to email.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# OTP Verification View
# -------------------------------
@extend_schema(
    tags=["Authentication"],
    request=VerifyOTPSerializer,
    responses={200: dict, 400: dict, 404: dict}
)
class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            if verify_otp(user, otp):
                refresh = RefreshToken.for_user(user)
                login(request, user)
                return Response({
                    'message': 'OTP verified successfully',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------
# User Location View
# -------------------------------
@extend_schema(
    tags=["User Location"],
    responses={200: LocationSerializer, 201: LocationSerializer, 400: dict}
)
class UserLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        location = request.user.locations.first()  # get first location
        if not location:
            return Response({'detail': 'Location not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        location = request.user.locations.first()
        if not location:
            return Response({'detail': 'Location not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Seller Profile View
# -------------------------------
@extend_schema(
    tags=["User Profile"],
    responses={200: SellerProfileSerializer, 400: dict}
)
class SellerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'seller':
            return Response({'detail': 'Only sellers have a profile.'}, status=status.HTTP_403_FORBIDDEN)
        seller_profile = getattr(request.user, 'seller_profile', None)
        if not seller_profile:
            return Response({'detail': 'Seller profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SellerProfileSerializer(seller_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        if request.user.role != 'seller':
            return Response({'detail': 'Only sellers can update their profile.'}, status=status.HTTP_403_FORBIDDEN)
        seller_profile = getattr(request.user, 'seller_profile', None)
        if not seller_profile:
            return Response({'detail': 'Seller profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SellerProfileSerializer(seller_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
