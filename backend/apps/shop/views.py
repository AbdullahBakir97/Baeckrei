from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders import slots

from . import config


@api_view(['GET'])
@permission_classes([AllowAny])
def info(request):
    """The shop's public details for the footer, contact page and Impressum."""
    shop = config.get()
    public = ('name', 'legal_name', 'owner', 'street', 'house_number', 'postal_code', 'city', 'country',
              'transit', 'phone', 'email', 'vat_id', 'register', 'instagram', 'facebook', 'twitter',
              'announcement', 'announcement_en', 'pickup_enabled', 'delivery_enabled')
    return Response({
        **{key: getattr(shop, key) for key in public},
        'delivery_fee': str(shop.delivery_fee),
        'hours': slots.opening_status(config=shop),
    })
