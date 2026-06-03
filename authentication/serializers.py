from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """Serializes the CustomUser model for profile details."""
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'email', 'role', 'purchased_products', 'created_at')
        read_only_fields = ('id', 'role', 'purchased_products', 'created_at')

class RegisterSerializer(serializers.ModelSerializer):
    """Validates registration details and creates a hashed User instance."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password')

    def validate_email(self, value):
        # Ensure email is unique
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Create user using the CustomUserManager to ensure password hashing
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user