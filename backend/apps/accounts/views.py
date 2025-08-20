from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)
from django.db.models import Count
from django.utils import timezone

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
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
                return Response({'error': 'Invalid old password'}, 
                            status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
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
