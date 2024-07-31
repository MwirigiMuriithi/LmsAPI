from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, ChangePasswordSerializer
from .permissions import IsAuthenticatedAndActive
from .models import CustomUser, EmailVerificationToken
from .utils import generate_token
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Create a verification token
        token = generate_token()
        expires_at = timezone.now() + timezone.timedelta(hours=1)  # Token valid for 1 hour
        EmailVerificationToken.objects.create(user=user, token=token, expires_at=expires_at)
        self.send_verification_email(user.email, token)

    def send_verification_email(self, email, token):
        verification_link = f"{settings.FRONTEND_URL}/verify-email/?token={token}&email={email}"
        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
        if user.is_verified:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'detail': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticatedAndActive]

@api_view(['GET'])
def verify_email(request):
    token = request.query_params.get('token')
    email = request.query_params.get('email')
    if not token or not email:
        return Response({'detail': 'Token and email are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token_record = EmailVerificationToken.objects.get(user__email=email, token=token)
        if token_record.is_expired():
            return Response({'detail': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = token_record.user
        user.is_verified = True
        user.save()
        token_record.delete()  # Delete token after verification
        return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)
    except EmailVerificationToken.DoesNotExist:
        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        old_password = serializer.validated_data['old_password']
        if not user.check_password(old_password):
            return Response({'old_password': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)
