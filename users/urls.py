from django.urls import path
from .user_auth_views import RegisterView, LoginView, UserView, VerifyOTPView, LogoutView
from .event_views import UpdateLocationView , NearbyEventsView, EventCreateView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserView.as_view(), name='user'),
    path('update-location/', UpdateLocationView.as_view(), name='update_location'),
    path('nearby-events/', NearbyEventsView.as_view(), name="nearby-events"),
    path('create-event/', EventCreateView.as_view(), name='create-event'),
]
