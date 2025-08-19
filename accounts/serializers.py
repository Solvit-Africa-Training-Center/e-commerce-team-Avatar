from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
