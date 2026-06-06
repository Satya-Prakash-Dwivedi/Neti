from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    """API endpoint for signing up new users."""
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(APIView):
    """API endpoint to get or update current authenticated user's profile."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
import os
import requests
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

class PasswordResetRequestView(APIView):
    """Handles password reset request, generates token and sends email via Brevo."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=email).first()
        if user:
            # Generate token and base64 encoded user ID
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Construct reset link based on the Origin header
            frontend_url = request.headers.get('Origin', 'https://dev.netiacademy.com')
            reset_link = f"{frontend_url}/reset-password?uidb64={uidb64}&token={token}"
            
            # Send email via Brevo API
            api_key = os.getenv('VITE_BREVO_API_KEY')
            sender_email = os.getenv('VITE_SENDER_EMAIL')
            
            if api_key and sender_email:
                headers = {
                    'accept': 'application/json',
                    'api-key': api_key,
                    'content-type': 'application/json'
                }
                data = {
                    "sender": {"email": sender_email, "name": "Netiacademy"},
                    "to": [{"email": user.email, "name": user.name}],
                    "subject": "Netiacademy - Password Reset",
                    "htmlContent": f"<html><body><h3>Hello {user.name},</h3><p>We received a request to reset your password. Click the link below to set a new password:</p><p><a href='{reset_link}'>{reset_link}</a></p><p>If you did not request this, please ignore this email.</p></body></html>"
                }
                try:
                    response = requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=data, timeout=10)
                    print(f"Brevo Response Status: {response.status_code}")
                    print(f"Brevo Response Body: {response.text}")
                    response.raise_for_status()
                except Exception as e:
                    print(f"Error sending Brevo email: {e}")
        
        # Always return 200 OK so we don't leak which emails exist in the database
        return Response({'message': 'If an account exists, a password reset email has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Handles actual password reset using the uidb64 and token."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uidb64, token, new_password]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
