from django.urls import path
from .user_auth_views import RegisterView, LoginView, UserView, VerifyOTPView, LogoutView
from .event_views import (
    UpdateLocationView,
    NearbyEventsView,
    EventCreateView,
    MyEventsView,
    EventJoinRequestView,
    RespondJoinRequestView,
    PendingJoinRequestsView
)
from .chat_views import GetChatGroupsView, GetChatMessagesView, SendChatMessageView

urlpatterns = [
    # User Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserView.as_view(), name='user'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Events
    path('update-location/', UpdateLocationView.as_view(), name='update_location'),
    path('nearby-events/', NearbyEventsView.as_view(), name="nearby-events"),
    path('create-event/', EventCreateView.as_view(), name='create-event'),
    path('my-events/', MyEventsView.as_view(), name='my-events'),

    # Event Join Requests
    path('join-request/<int:event_id>/', EventJoinRequestView.as_view(), name='join-request'),
    path('respond-join-request/<int:request_id>/', RespondJoinRequestView.as_view(), name='respond-join-request'),
    path('event-requests/<int:event_id>/pending/', PendingJoinRequestsView.as_view(), name='pending-requests'),
    
    # Chat
    path('chat/groups/', GetChatGroupsView.as_view(), name='chat-groups'),
    path('chat/<int:chat_group_id>/messages/', GetChatMessagesView.as_view(), name='chat-messages'),
    path('chat/<int:chat_group_id>/send/', SendChatMessageView.as_view(), name='send-message'),
]
