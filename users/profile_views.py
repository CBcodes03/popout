from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
import base64
import re

class UpdateProfileView(APIView):
    """Update user profile (bio and profile picture)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Update bio if provided
        if "bio" in request.data:
            user.bio = request.data.get("bio", "")
        
        # Update profile picture if provided
        if "profile_picture" in request.data:
            profile_picture_data = request.data.get("profile_picture")
            
            # Handle base64 image data
            if profile_picture_data and isinstance(profile_picture_data, str) and profile_picture_data.startswith("data:image"):
                try:
                    # Extract base64 data
                    header, encoded = profile_picture_data.split(",", 1)
                    image_data = base64.b64decode(encoded)
                    
                    # Determine file extension from header
                    ext = "png"
                    if "jpeg" in header or "jpg" in header:
                        ext = "jpg"
                    elif "gif" in header:
                        ext = "gif"
                    elif "webp" in header:
                        ext = "webp"
                    
                    # Save file
                    filename = f"user_{user.id}_profile.{ext}"
                    user.profile_picture.save(
                        filename,
                        ContentFile(image_data),
                        save=False
                    )
                except Exception as e:
                    return Response({"error": f"Failed to process image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.save()
        
        return Response({
            "message": "Profile updated successfully",
            "bio": user.bio,
            "profile_picture": user.profile_picture.url if user.profile_picture else None
        }, status=status.HTTP_200_OK)

