import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, Payment
from django.conf import settings
from .serializers import OrderSerializer, CheckoutSerializer
from .services import OrderService, CheckoutError
from apps.accounts.models import Customer
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

    def get_permissions(self):
        # Customers place orders through `checkout`; creating orders directly
        # and deleting them is staff-only.
        if self.action in ('create', 'destroy'):
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # The owner always comes from the authenticated user, never the payload.
        serializer.save(customer=self._customer())

    def _customer(self):
        customer, _ = Customer.objects.get_or_create(
            user=self.request.user,
            defaults={'customer_id': uuid.uuid4().hex},
        )
        return customer

    @action(detail=False, methods=['get'])
    def checkout_options(self, request):
        """Fulfilment and payment choices for the checkout page."""
        return Response({
            'vat_rate': str(settings.VAT_RATE),
            'fulfillment_methods': [
                {'code': Order.FulfillmentChoices.PICKUP, 'label': 'Pickup in store', 'fee': '0.00'},
                {'code': Order.FulfillmentChoices.DELIVERY, 'label': 'Delivery', 'fee': str(settings.DELIVERY_FEE)},
            ],
            'payment_methods': [
                {'code': Payment.PaymentMethod.CASH, 'label': 'Cash on pickup or delivery', 'available': True},
                {'code': Payment.PaymentMethod.CREDIT_CARD, 'label': 'Card on pickup or delivery', 'available': True},
                {'code': Payment.PaymentMethod.PAYPAL, 'label': 'PayPal', 'available': settings.PAYPAL_ENABLED},
            ],
        })

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Place an order from the current user's cart."""
        from apps.cart.controllers.CMC import CartManagementController

        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart, _ = CartManagementController().get_or_create_cart(request)
        try:
            order = OrderService.checkout(self._customer(), cart, serializer.validated_data)
        except CheckoutError as e:
            return Response(
                {'status': 'error', 'error_type': e.code, 'detail': {'message': e.message, **e.extra}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(OrderSerializer(order, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Let the order's owner (or staff) cancel an order that is still cancelable."""
        order = self.get_object()
        if not order.is_cancelable:
            return Response(
                {'error': 'This order can no longer be canceled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order = OrderService.update_order_status(order, Order.StatusChoices.CANCELED)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
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