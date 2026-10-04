"""Everything a menu screen shows, in one response."""
from django.utils import timezone

from apps.orders import slots
from apps.products.models import Category, Product
from apps.products.serializers import ProductListSerializer
from apps.shop import config as shop_config

from .models import MenuScreen
from .serializers import PublicScreenSerializer, PublicSlideSerializer


def default_screen():
    """The screen at /menu-board: the one marked default, else the first."""
    screen = MenuScreen.objects.filter(is_default=True).first() or MenuScreen.objects.first()
    return screen or MenuScreen(name='Menü', slug='default')


def board_payload(screen, request, now=None):
    now = now or timezone.now()
    shop = shop_config.get()

    categories = list(Category.objects.filter(is_active=True).order_by('order', 'name'))
    if screen.categories:
        wanted = [str(c) for c in screen.categories]
        categories = sorted((c for c in categories if str(c.pk) in wanted), key=lambda c: wanted.index(str(c.pk)))

    products = (Product.objects.filter(status='active', available=True, category__in=categories)
                .select_related('category').order_by('name'))
    hidden = {str(p) for p in screen.hidden_products or []}
    products = [p for p in products if str(p.pk) not in hidden]
    if screen.sold_out == MenuScreen.SoldOut.HIDE:
        products = [p for p in products if p.stock > 0]
    present = {str(p.pk) for p in products}

    slides = screen.slides.select_related('product') if screen.pk else []
    return {
        'screen': PublicScreenSerializer(screen, context={'request': request}).data,
        'categories': [{'id': c.pk, 'slug': c.slug, 'name': c.name, 'name_en': c.name_en} for c in categories],
        'products': ProductListSerializer(products, many=True, context={'request': request}).data,
        'featured': [str(p) for p in screen.featured_products or [] if str(p) in present],
        'slides': PublicSlideSerializer([s for s in slides if s.runs_at(now)], many=True, context={'request': request}).data,
        'status': slots.opening_status(now=now, config=shop),
        'shop': {
            'name': shop.name,
            'address': shop_config.address_line(shop),
            'time_zone': str(timezone.get_current_timezone()),
        },
        'server_time': now.isoformat(),
    }
