from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, SellerProfile, Location

# -------------------------------
# User Registration Serializer
# -------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    country = serializers.CharField(required=True)
    state = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=True)
    street_address = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("email", "full_name", "password", "role", "country", "state", "city", "street_address")

    def create(self, validated_data):
        # Extract location data
        country = validated_data.pop("country")
        state = validated_data.pop("state", "")
        city = validated_data.pop("city")
        street_address = validated_data.pop("street_address")

        # Create the user
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            password=validated_data["password"],
            role=validated_data.get("role", "client"),
        )

        # Automatically create the location
        Location.objects.create(
            user=user,
            country=country,
            state=state,
            city=city,
            street_address=street_address
        )

        return user


# -------------------------------
# OTP Verification Serializer
# -------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


# -------------------------------
# User Profile Serializer
# -------------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role"]
        read_only_fields = ["id", "email", "role"]


# -------------------------------
# Seller Profile Serializer
# -------------------------------
class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = [
            "id",
            "user",
            "store_name",
            "store_logo",
            "is_approved",
            "created_at",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]
        read_only_fields = ["id", "created_at", "is_deleted", "deleted_at", "deleted_by"]


# -------------------------------
# Location Serializer
# -------------------------------
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "user", "country", "state", "city", "street_address"]
        read_only_fields = ["id", "user"]


# -------------------------------
# User Login Serializer (from upstream)
# -------------------------------
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials!")
