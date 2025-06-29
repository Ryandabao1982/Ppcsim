from rest_framework import serializers
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm password', style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': False, 'allow_blank': True} # Consistent with model
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        # You can add more password validation here if needed (e.g., complexity)
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') # We don't need password2 for creating user model
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            # username is optional, provide if present, else model handles it
            username=validated_data.get('username', None)
        )
        return user

class UserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for user details (read-only).
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_joined', 'is_active')
        read_only_fields = fields # All fields are read-only for this serializer
