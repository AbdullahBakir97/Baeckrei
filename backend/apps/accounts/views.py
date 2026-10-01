from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import uuid

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import ProtectedError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Address, Customer
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    AddressSerializer,
    AdminUserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from django.db.models import Count, Q
from django.utils import timezone

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'register':
            return [AllowAny()]
        # Creating or deleting arbitrary accounts is reserved for staff;
        # customers sign up through `register`.
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        # Non-staff users can only ever see or modify their own account.
        if not self.request.user.is_staff:
            return User.objects.filter(pk=self.request.user.pk)
        queryset = User.objects.annotate(order_count=Count('customer__customer_orders')).order_by('-date_joined')
        term = self.request.query_params.get('search')
        if term:
            queryset = queryset.filter(
                Q(email__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term)
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        if self.request.user.is_staff and self.action in ('list', 'retrieve', 'update', 'partial_update'):
            return AdminUserSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Store current session key before registration
            current_session_key = request.session.session_key
            if current_session_key:
                request.session['_auth_user_pre_login_session_key'] = current_session_key
                request.session.save()

            # Create user and customer
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            # Force authentication to trigger cart merging signal
            from django.contrib.auth import login
            login(request, user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': _('Invalid old password')}, 
                            status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': _('Password updated successfully')})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': _('Successfully logged out')})
        except Exception:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def dashboard_stats(self, request):
        """Get dashboard statistics."""
        try:
            total_users = User.objects.count()
            
            # Get today's stats
            today = timezone.now().date()
            today_users = User.objects.filter(date_joined__date=today).count()

            return Response({
                'total_users': total_users,
                'today_users': today_users
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddressViewSet(viewsets.ModelViewSet):
    """The signed-in customer's saved delivery addresses."""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def _customer(self):
        customer, _created = Customer.objects.get_or_create(
            user=self.request.user, defaults={'customer_id': uuid.uuid4().hex}
        )
        return customer

    def get_queryset(self):
        return Address.objects.filter(customer__user=self.request.user, saved=True).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(customer=self._customer(), saved=True)

    def perform_destroy(self, instance):
        # Past orders keep pointing at the address, so only hide it then.
        try:
            instance.delete()
        except ProtectedError:
            instance.saved = False
            instance.save(update_fields=['saved', 'updated_at'])


class PasswordResetRequestView(APIView):
    """Email a password reset link. Always answers the same way so the
    endpoint cannot be used to find out which emails have accounts."""
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data['email'], is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/{uid}/{token}"
            send_mail(
                subject='Reset your password',
                message=(
                    'We received a request to reset your password.\n\n'
                    f'Choose a new password here: {link}\n\n'
                    "If you didn't ask for this, you can ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        return Response({'message': _('If an account exists for this email, we sent a reset link.')})


class PasswordResetConfirmView(APIView):
    """Set a new password using the uid and token from the reset link."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(data['uid'])), is_active=True)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None
        if user is None or not default_token_generator.check_token(user, data['token']):
            return Response(
                {'detail': _('This reset link is invalid or has expired. Please request a new one.')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(data['new_password'])
        user.save(update_fields=['password'])
        return Response({'message': _('Your password has been changed. You can now sign in.')})
