from rest_framework import serializers
from django.conf import settings
from auth_system.models import Account
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group
from auth_system.services.auth import build_user_payload
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

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
