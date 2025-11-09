from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, OTPVerifySerializer, EmailTokenObtainPairSerializer
from .utils import genotp, send_vmail, store_otp, validate_otp

User = get_user_model()

# --------------------------
# Register User (send OTP)
# --------------------------
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            otp = genotp()
            store_otp(email, otp, password)
            send_vmail(otp, email)

            return Response({"message": "OTP sent to your email. Valid for 300 seconds. (5 min)"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Verify OTP & Create User
# --------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp_input = serializer.validated_data["otp"]

            is_valid, result = validate_otp(email, otp_input)
            if not is_valid:
                return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)

            password = result  # retrieved from in-memory store
            username = email.split('@')[0]
            User.objects.create_user(username=username, email=email, password=password)

            return Response({"message": "Registration successful!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Login (JWT)
# --------------------------
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            data['message'] = "Login successful!"
            return Response(data, status=status.HTTP_200_OK)
        return response


# --------------------------
# Logout (optional blacklist)
# --------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# --------------------------
# Get logged-in user info
# --------------------------
class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "location": getattr(user, "location", None),
            "bio": getattr(user, "bio", None) or "",
            "profile_image": user.profile_picture.url if user.profile_picture else None,
        })
