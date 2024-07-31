from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, EmailVerificationToken
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .utils import generate_token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'is_student', 'is_lecturer')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_student=validated_data.get('is_student', False),
            is_lecturer=validated_data.get('is_lecturer', False)
        )   
        # Create a verification token
        token = generate_token()
        expires_at = timezone.now() + timezone.timedelta(hours=1)  # Token valid for 1 hour
        EmailVerificationToken.objects.create(user=user, token=token, expires_at=expires_at)
        self.send_verification_email(user.email, token)
        return user
    def send_verification_email(self, email, token):
        verification_link = f"{settings.FRONTEND_URL}/verify-email/?token={token}&email={email}"
        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords must match"})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
