from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from .serializers import OrderSerializer
from .services import OrderService
from django.db.models import Count, Sum
from django.utils import timezone

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer__user=user)

    @action(detail=True, methods=['post'])
    def add_tracking(self, request, pk=None):
        order = self.get_object()
        tracking_number = request.data.get('tracking_number')
        
        if not tracking_number:
            return Response(
                {'error': 'Tracking number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            order = OrderService.add_tracking_number(order, tracking_number)
            return Response(OrderSerializer(order).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        try:
            order = OrderService.update_order_status(order, new_status)
            return Response(OrderSerializer(order).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def dashboard_stats(self, request):
        """Get dashboard statistics."""
        try:
            # Get counts
            total_orders = Order.objects.count()
            
            # Get revenue
            total_revenue = Order.objects.filter(status='completed').aggregate(
                total=Sum('total')
            )['total'] or 0
            
            # Get today's stats
            today = timezone.now().date()
            today_orders = Order.objects.filter(created_at__date=today).count()
            today_revenue = Order.objects.filter(
                created_at__date=today,
                status='completed'
            ).aggregate(total=Sum('total'))['total'] or 0

            return Response({
                'total_orders': total_orders,
                'total_revenue': str(total_revenue),
                'today_orders': today_orders,
                'today_revenue': str(today_revenue)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def recent_orders(self, request):
        """Get recent orders."""
        try:
            recent_orders = Order.objects.order_by('-created_at')[:5]
            orders_data = [{
                'id': order.id,
                'customer_email': order.customer.email,
                'total': str(order.total),
                'status': order.status,
                'created_at': order.created_at
            } for order in recent_orders]
            
            return Response(orders_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )