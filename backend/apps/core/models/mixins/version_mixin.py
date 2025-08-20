from django.db import models
from ...exceptions import VersionConflictError as VersionConflict

class VersionMixin(models.Model):
    """Mixin class for version-controlled models."""
    version = models.IntegerField(default=1, help_text="Optimistic locking version")
    
    class Meta:
        abstract = True
        
    def increment_version(self, using=None):
        """Atomic version increment."""
        cls = self.__class__
        cls.objects.filter(pk=self.pk).update(version=models.F('version') + 1)
        self.version = cls.objects.get(pk=self.pk).version
        
    def check_version(self, expected_version: int) -> None:
        """Check version matches expected."""
        if self.version != expected_version:
            raise VersionConflict(
                f"{self._meta.model_name} version mismatch",
                obj_type=self._meta.model_name,
                obj_id=self.pk
            )
            
    def save_with_version(self, **kwargs):
        """Save with version check."""
        if 'update_fields' in kwargs and 'version' not in kwargs['update_fields']:
            kwargs['update_fields'].append('version')
        self._do_pre_save_version_checks()
        super().save(**kwargs)
        
    def atomic_version_update(self):
        """Atomic version increment with validation."""
        self.check_version(self.version)
        self.increment_version()
        
    def _do_pre_save_version_checks(self) -> None:
        """Comprehensive version validation for enterprise scenarios"""
        if not hasattr(self, 'version'):
            raise AttributeError("Version field required for versioned models")
            
        if self.version < 1:
            raise ValidationError({
                'version': 'Version cannot be less than 1',
                'code': 'version_rollback'
            })
            
        if self.version > 1000000:  # Prevent integer overflow scenarios
            raise ValidationError({
                'version': 'Version number exceeds maximum allowed value',
                'code': 'version_overflow'
            })
            
        try:
            current_version = type(self).objects.values_list(
                'version', flat=True
            ).get(pk=self.pk)
            
            if self.version != current_version + 1:
                raise ValidationError({
                    'version': 'Version must increment by 1',
                    'code': 'version_increment'
                })
                
        except ObjectDoesNotExist:
            pass  # New instance creation
