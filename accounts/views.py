# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from .models import User
from .serializers import RegisterSerializer, VerifyOTPSerializer
from .utils import send_otp_email, verify_otp
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Authentication"],
               request=RegisterSerializer,   
    responses={201: dict, 400: dict}
               )
class RegisterView(APIView):
    """
    Register a new user and send OTP to their email.
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user)  # use utils.py function
            return Response(
                {'message': 'User registered successfully. OTP sent to email.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Authentication"],
               request=VerifyOTPSerializer,
               responses={200: dict, 400: dict, 404: dict}
               )
class VerifyOTPView(APIView):
    """
    Verify OTP code for a user. Marks user as verified and returns JWT tokens.
    """
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            if verify_otp(user, otp):  # use utils.py function
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
