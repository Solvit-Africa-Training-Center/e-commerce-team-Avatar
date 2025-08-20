# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import RegisterSerializer, VerifyOTPSerializer, UserLoginSerializer
from .utils import send_otp_email, verify_otp
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

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

@extend_schema(tags=["Authentication"])
class UserLoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = RegisterSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh":str(token),  
                          "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)

@extend_schema(tags=["Authentication"],  responses={
        205: dict,  
        400: dict,  
        401: dict 
    },)
class UserLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # 1. Extract access token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response({"detail": "Authorization header missing or invalid"},
                                status=status.HTTP_400_BAD_REQUEST)

            access_token_str = auth_header.split(" ")[1]
            access_token = AccessToken(access_token_str)

            # 2. Try to blacklist this access token (if tracked in OutstandingToken)
            outstanding_qs = OutstandingToken.objects.filter(token=access_token_str)
            if outstanding_qs.exists():
                for token in outstanding_qs:
                    BlacklistedToken.objects.get_or_create(token=token)

            # 3. Blacklist all outstanding refresh tokens for this user
            user_tokens = OutstandingToken.objects.filter(user=request.user)
            for token in user_tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Authentication"])
class TokenRefreshView(TokenRefreshView):
    pass
