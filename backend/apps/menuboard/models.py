"""Menu screens for the TVs in the shop, designed in the admin.

Each screen has its own address (/menu-board/<slug>) and a 4-digit code: on
a TV, open /tv and type the code once. The screen reads its design and the
live menu from the public board API every minute, reports when it was last
seen, and reloads when the admin asks it to.
"""
import random

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def _new_code():
    for _attempt in range(50):
        code = f'{random.randint(0, 9999):04d}'
        if not MenuScreen.objects.filter(code=code).exists():
            return code
    raise RuntimeError('No free screen code')


class MenuScreen(models.Model):
    class Layout(models.TextChoices):
        COLUMNS = 'columns', 'Feature and columns'
        GRID = 'grid', 'Photo grid'
        LIST = 'list', 'Classic list'
        SPOTLIGHT = 'spotlight', 'One product at a time'

    class Theme(models.TextChoices):
        OVEN = 'oven', 'Oven (dark)'
        PAPER = 'paper', 'Paper (light)'
        ESPRESSO = 'espresso', 'Espresso'
        SAGE = 'sage', 'Sage'
        CUSTOM = 'custom', 'Custom colours'

    class Language(models.TextChoices):
        GERMAN = 'de', 'German'
        ENGLISH = 'en', 'English'
        ARABIC = 'ar', 'Arabic'
        ALTERNATE = 'alternate', 'German and English'
        GERMAN_ARABIC = 'de_ar', 'German and Arabic'

    class Orientation(models.TextChoices):
        AUTO = 'auto', 'Automatic'
        ROTATE_RIGHT = 'rotate-right', 'TV turned upright (rotate right)'
        ROTATE_LEFT = 'rotate-left', 'TV turned upright (rotate left)'

    class SoldOut(models.TextChoices):
        MARK = 'mark', 'Show as sold out'
        HIDE = 'hide', 'Hide'

    class Font(models.TextChoices):
        SERIF = 'serif', 'Elegant serif'
        SANS = 'sans', 'Modern sans'

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    code = models.CharField(max_length=4, unique=True, blank=True)
    is_default = models.BooleanField(default=False, help_text='Shown at /menu-board without a name')

    # Design
    layout = models.CharField(max_length=20, choices=Layout.choices, default=Layout.COLUMNS)
    theme = models.CharField(max_length=20, choices=Theme.choices, default=Theme.OVEN)
    font = models.CharField(max_length=10, choices=Font.choices, default=Font.SERIF)
    background_color = models.CharField(max_length=7, blank=True)
    text_color = models.CharField(max_length=7, blank=True)
    accent_color = models.CharField(max_length=7, blank=True)
    background_image = models.ImageField(upload_to='menu-screens/', blank=True, null=True)
    background_dim = models.PositiveSmallIntegerField(default=60, help_text='How much the background photo is darkened, 0–90 %')
    orientation = models.CharField(max_length=20, choices=Orientation.choices, default=Orientation.AUTO)
    language = models.CharField(max_length=10, choices=Language.choices, default=Language.GERMAN)

    # Content
    headline = models.CharField(max_length=120, blank=True)
    headline_en = models.CharField(max_length=120, blank=True)
    headline_ar = models.CharField(max_length=120, blank=True)
    ticker = models.CharField(max_length=300, blank=True, help_text='A running message along the bottom')
    ticker_en = models.CharField(max_length=300, blank=True)
    ticker_ar = models.CharField(max_length=300, blank=True)
    categories = models.JSONField(default=list, blank=True, help_text='Category ids in order; empty: all')
    featured_products = models.JSONField(default=list, blank=True, help_text='Product ids for the large spot; empty: automatic')
    hidden_products = models.JSONField(default=list, blank=True)
    show_prices = models.BooleanField(default=True)
    show_descriptions = models.BooleanField(default=True)
    show_images = models.BooleanField(default=True)
    show_tags = models.BooleanField(default=True)
    show_qr = models.BooleanField(default=True)
    show_clock = models.BooleanField(default=True)
    show_status = models.BooleanField(default=True)
    sold_out = models.CharField(max_length=10, choices=SoldOut.choices, default=SoldOut.MARK)
    page_seconds = models.PositiveSmallIntegerField(default=12)
    slide_every = models.PositiveSmallIntegerField(default=2, help_text='Show a promotion after this many menu pages')

    # Device
    reload_token = models.PositiveIntegerField(default=0)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_info = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'screen'
            slug, n = base, 2
            while MenuScreen.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f'{base}-{n}', n + 1
            self.slug = slug
        if not self.code:
            self.code = _new_code()
        self.background_dim = min(self.background_dim, 90)
        self.page_seconds = max(self.page_seconds, 5)
        super().save(*args, **kwargs)
        if self.is_default:
            MenuScreen.objects.exclude(pk=self.pk).filter(is_default=True).update(is_default=False)

    @property
    def online(self):
        # Screens check in every minute.
        return bool(self.last_seen_at and timezone.now() - self.last_seen_at < timezone.timedelta(minutes=3))

    def __str__(self):
        return self.name


class MenuSlide(models.Model):
    """A full-screen promotion shown between the menu pages."""

    class Style(models.TextChoices):
        PHOTO = 'photo', 'Photo with text'
        PRODUCT = 'product', 'Product highlight'
        TEXT = 'text', 'Big message'

    screen = models.ForeignKey(MenuScreen, on_delete=models.CASCADE, related_name='slides')
    style = models.CharField(max_length=10, choices=Style.choices, default=Style.PRODUCT)
    title = models.CharField(max_length=120)
    title_en = models.CharField(max_length=120, blank=True)
    title_ar = models.CharField(max_length=120, blank=True)
    text = models.CharField(max_length=300, blank=True)
    text_en = models.CharField(max_length=300, blank=True)
    text_ar = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    price_note = models.CharField(max_length=60, blank=True, help_text='e.g. "instead of 5.40 €"')
    price_note_en = models.CharField(max_length=60, blank=True)
    price_note_ar = models.CharField(max_length=60, blank=True)
    image = models.ImageField(upload_to='menu-screens/slides/', blank=True, null=True)
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    seconds = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Empty: the screen's page time")
    # When the slide runs; all optional.
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    weekdays = models.JSONField(default=list, blank=True, help_text='0 = Monday; empty: every day')

    class Meta:
        ordering = ['order', 'id']

    def runs_at(self, moment):
        local = timezone.localtime(moment)
        if not self.active:
            return False
        if self.start_date and local.date() < self.start_date:
            return False
        if self.end_date and local.date() > self.end_date:
            return False
        if self.weekdays and local.weekday() not in self.weekdays:
            return False
        if self.start_time and local.time() < self.start_time:
            return False
        if self.end_time and local.time() >= self.end_time:
            return False
        return True

    def __str__(self):
        return self.title
