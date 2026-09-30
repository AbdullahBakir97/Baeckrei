import uuid

from django.utils.translation import gettext as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, Payment
from django.conf import settings
from .serializers import OrderSerializer, CheckoutSerializer
from .services import OrderService, CheckoutError
from apps.accounts.models import Customer
from django.db.models import Count, Sum, Q
from django.utils import timezone

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.select_related('customer__user', 'address', 'order_payment') \
            .prefetch_related('order_items__product')
        if not user.is_staff:
            return queryset.filter(customer__user=user)

        # Filters used by the admin order list.
        params = self.request.query_params
        if params.get('status'):
            queryset = queryset.filter(status=params['status'])
        if params.get('fulfillment_method'):
            queryset = queryset.filter(fulfillment_method=params['fulfillment_method'])
        if params.get('start_date'):
            queryset = queryset.filter(created_at__date__gte=params['start_date'])
        if params.get('end_date'):
            queryset = queryset.filter(created_at__date__lte=params['end_date'])
        if params.get('search'):
            term = params['search']
            queryset = queryset.filter(
                Q(order_number__icontains=term) | Q(customer__user__email__icontains=term)
                | Q(customer__user__first_name__icontains=term) | Q(customer__user__last_name__icontains=term)
            )
        return queryset

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
        customer, _created = Customer.objects.get_or_create(
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
        cart, _created = CartManagementController().get_or_create_cart(request)
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
                {'error': _('This order can no longer be canceled')},
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
        """Order counts and revenue for the admin dashboard."""
        completed = Order.objects.filter(status=Order.StatusChoices.COMPLETED)
        today = timezone.localdate()
        return Response({
            'total_orders': Order.objects.count(),
            'open_orders': Order.objects.filter(
                status__in=[Order.StatusChoices.PENDING, Order.StatusChoices.PROCESSING]
            ).count(),
            'total_revenue': str(completed.aggregate(total=Sum('total_price'))['total'] or 0),
            'today_orders': Order.objects.filter(created_at__date=today).count(),
            'today_revenue': str(
                completed.filter(created_at__date=today).aggregate(total=Sum('total_price'))['total'] or 0
            ),
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def recent_orders(self, request):
        """The five newest orders for the admin dashboard."""
        recent = Order.objects.select_related('customer__user').order_by('-created_at')[:5]
        return Response([{
            'id': order.id,
            'order_number': order.order_number,
            'customer_email': order.customer.user.email if order.customer.user else '',
            'total': str(order.total_price),
            'status': order.status,
            'fulfillment_method': order.fulfillment_method,
            'created_at': order.created_at,
        } for order in recent])
