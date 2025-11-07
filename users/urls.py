from django.urls import path
from .user_auth_views import RegisterView, LoginView, UserView, VerifyOTPView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserView.as_view(), name='user'),
]
