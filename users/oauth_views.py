from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import requests
import json
from urllib.parse import urlencode

User = get_user_model()


class GoogleOAuthView(APIView):
    """Initiate Google OAuth flow"""
    permission_classes = [AllowAny]

    def get(self, request):
        # Google OAuth configuration
        client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', '')
        redirect_uri = request.build_absolute_uri('/api/oauth/google/callback/')
        
        if not client_id:
            return Response({
                "error": "Google OAuth not configured. Please set GOOGLE_OAUTH2_CLIENT_ID in settings."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Google OAuth scopes
        scope = 'openid email profile'
        
        # Build Google OAuth URL
        auth_url = (
            'https://accounts.google.com/o/oauth2/v2/auth?'
            f'client_id={client_id}&'
            f'redirect_uri={redirect_uri}&'
            f'response_type=code&'
            f'scope={scope}&'
            f'access_type=offline&'
            f'prompt=consent'
        )
        
        return Response({
            "auth_url": auth_url
        }, status=status.HTTP_200_OK)


class GoogleOAuthCallbackView(APIView):
    """Handle Google OAuth callback and create/login user"""
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')
        
        if error:
            return Response({
                "error": f"OAuth error: {error}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not code:
            return Response({
                "error": "Authorization code not provided"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Exchange code for access token
            client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', '')
            client_secret = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', '')
            redirect_uri = request.build_absolute_uri('/api/oauth/google/callback/')
            
            if not client_id or not client_secret:
                return Response({
                    "error": "Google OAuth not properly configured"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Exchange authorization code for tokens
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            access_token = tokens.get('access_token')
            if not access_token:
                return Response({
                    "error": "Failed to obtain access token"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user info from Google
            user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_response = requests.get(user_info_url, headers=headers)
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            
            # Extract user data
            email = user_info.get('email')
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            picture = user_info.get('picture')
            google_id = user_info.get('id')
            
            if not email:
                return Response({
                    "error": "Email not provided by Google"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            username = email.split('@')[0]
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'verified': True,  # OAuth users are verified
                }
            )
            
            # Update user info if not new
            if not created:
                if first_name and not user.first_name:
                    user.first_name = first_name
                if last_name and not user.last_name:
                    user.last_name = last_name
                if not user.verified:
                    user.verified = True
                user.save()
            
            # Update profile picture if available
            if picture and not user.profile_picture:
                try:
                    import urllib.request
                    from django.core.files.base import ContentFile
                    from django.core.files import File
                    
                    img_response = requests.get(picture)
                    if img_response.status_code == 200:
                        user.profile_picture.save(
                            f'google_{user.id}.jpg',
                            ContentFile(img_response.content),
                            save=True
                        )
                except Exception as e:
                    # If profile picture fails, continue without it
                    pass
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Login successful!" if not created else "Registration successful!",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            return Response({
                "error": f"OAuth request failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



