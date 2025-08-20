"""Mixin to add created_at and updated_at fields to models."""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
