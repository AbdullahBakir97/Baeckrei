"""Settings the bakery manages itself in the admin: business details,
opening hours, closing days and how pickup and delivery work.

Every field may be left empty; the server settings (SHOP_* in the
environment) are used then, so a fresh install works without any setup.
"""
from django.db import models


class ShopSettings(models.Model):
    """There is only one row (pk=1); use ShopSettings.load()."""
    # Business and contact details, shown in the footer, on the contact page,
    # in emails and in the Impressum.
    name = models.CharField(max_length=100, blank=True)
    legal_name = models.CharField(max_length=150, blank=True)
    owner = models.CharField(max_length=150, blank=True)
    street = models.CharField(max_length=150, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    transit = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    vat_id = models.CharField(max_length=50, blank=True)
    register = models.CharField(max_length=150, blank=True)
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    notification_email = models.EmailField(blank=True, help_text='Receives new orders and contact messages')

    # {"0": [["07:00", "18:00"]], ...} with 0 = Monday. Empty: SHOP_OPENING_HOURS.
    opening_hours = models.JSONField(default=dict, blank=True)

    pickup_enabled = models.BooleanField(default=True)
    delivery_enabled = models.BooleanField(default=True)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pickup_lead_minutes = models.PositiveIntegerField(null=True, blank=True)
    delivery_lead_minutes = models.PositiveIntegerField(null=True, blank=True)
    slot_minutes = models.PositiveIntegerField(null=True, blank=True)
    slot_days = models.PositiveIntegerField(null=True, blank=True)
    slot_capacity = models.PositiveIntegerField(null=True, blank=True)

    # A short notice shown at the top of the shop, e.g. holidays.
    announcement = models.CharField(max_length=300, blank=True)
    announcement_en = models.CharField(max_length=300, blank=True)
    announcement_active = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shop settings'
        verbose_name_plural = 'Shop settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.filter(pk=1).first() or cls(pk=1)

    def __str__(self):
        return 'Shop settings'


class ClosingDay(models.Model):
    """A day (or several) the shop is closed, e.g. holidays or a trade fair."""
    start = models.DateField()
    end = models.DateField(null=True, blank=True, help_text='Empty: closed on the start day only')
    label = models.CharField(max_length=150, blank=True)
    label_en = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['start']

    @property
    def last_day(self):
        return self.end or self.start

    def covers(self, day):
        return self.start <= day <= self.last_day

    def __str__(self):
        return f'{self.start}–{self.last_day} {self.label}'.strip()
