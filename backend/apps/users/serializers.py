from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Public/standard representation of user details."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'is_active',
            'is_staff',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_staff', 'created_at', 'updated_at']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT Token Serializer embedding user profile payload into the login response."""

    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the JWT payload
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Include serialized user info alongside tokens
        data['user'] = UserSerializer(self.user).data
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer ensuring valid credentials and preventing role escalation."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # All public registrations default securely to USER role
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=User.Role.USER
        )
        return user


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer used exclusively by Admins to modify user role and account status."""

    class Meta:
        model = User
        fields = ['role', 'is_active', 'first_name', 'last_name']

    def validate_role(self, value):
        if value not in [choice[0] for choice in User.Role.choices]:
            raise serializers.ValidationError(f"Invalid role '{value}'. Must be USER, AGENT, or ADMIN.")
        return value
