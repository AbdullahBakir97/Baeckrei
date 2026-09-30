from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import Address, Customer
import uuid

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_admin'] = user.is_admin
        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 
                 'phone', 'date_joined', 'last_login', 'is_active', 'is_admin')
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_active', 'is_admin')

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'This field is required.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', '')
        )
        return user

    def update(self, instance, validated_data):
        # Passwords may only be changed through `change_password`, which
        # verifies the old password first.
        if 'password' in validated_data:
            raise serializers.ValidationError(
                {'password': 'Use the change_password endpoint to change your password.'}
            )
        return super().update(instance, validated_data)

class AdminUserSerializer(serializers.ModelSerializer):
    """What staff see and may change about other users."""
    order_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'date_joined',
                  'last_login', 'is_active', 'is_staff', 'is_admin', 'order_count')
        read_only_fields = ('id', 'email', 'date_joined', 'last_login', 'is_admin', 'order_count')

    def get_order_count(self, obj):
        return getattr(obj, 'order_count', None)

    def validate(self, attrs):
        request = self.context.get('request')
        if request and self.instance == request.user:
            if attrs.get('is_active') is False or attrs.get('is_staff') is False:
                raise serializers.ValidationError(_('You cannot deactivate or demote your own account.'))
        return attrs

    def update(self, instance, validated_data):
        # The shop's admin UI checks is_admin; DRF permissions check is_staff.
        if 'is_staff' in validated_data:
            validated_data['is_admin'] = validated_data['is_staff']
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )
        # Create customer for the user
        Customer.objects.create(
            user=user,
            customer_id=str(uuid.uuid4())
        )
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class AddressSerializer(serializers.ModelSerializer):
    state = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    country = serializers.CharField(max_length=100, required=False, default='DE')

    class Meta:
        model = Address
        fields = ['id', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country']
        read_only_fields = ['id']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer data."""
    user = UserSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'customer_id', 'user', 'addresses', 'name', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_id', 'user', 'addresses', 'name', 'email', 'created_at', 'updated_at']
