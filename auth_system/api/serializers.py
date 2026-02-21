from rest_framework import serializers
from django.conf import settings
from auth_system.models import Account
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group
from auth_system.services.auth import build_user_payload
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from allauth.account.models import EmailAddress
from rest_framework.exceptions import AuthenticationFailed


class UserPayloadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    roles = serializers.ListField(child=serializers.CharField())

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # Sprawdź weryfikację e-maila, jeśli jest wymagana
        if getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', 'none') == 'mandatory':
            email_address = EmailAddress.objects.filter(user=self.user, email=self.user.email).first()
            if not email_address or not email_address.verified:
                raise AuthenticationFailed("Adres e-mail nie został zweryfikowany. Sprawdź swoją skrzynkę email.")

        data["expires_in"] = int(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        data["user"] = build_user_payload(self.user)

        return data


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("email", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        try:
            validate_password(value)  # Uruchamiamy walidację hasła z Django
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        return value

    def create(self, validated_data):
        user = Account.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
        group, _ = Group.objects.get_or_create(name="USER")
        user.groups.add(group)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["expires_in"] = int(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )

        return data

class GoogleOneTapSerializer(serializers.Serializer):
    credential = serializers.CharField()

class JWTResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = UserPayloadSerializer()

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    details = serializers.CharField(required=False)
