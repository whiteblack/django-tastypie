import datetime
import hmac
import time
from django.conf import settings
from django.db import models
try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


class ApiAccess(models.Model):
    """A simple model for use with the ``CacheDBThrottle`` behaviors."""
    identifier = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default='')
    request_method = models.CharField(max_length=10, blank=True, default='')
    accessed = models.PositiveIntegerField()
    
    def __unicode__(self):
        return u"%s @ %s" % (self.identifer, self.accessed)
    
    def save(self, *args, **kwargs):
        self.accessed = int(time.time())
        return super(ApiAccess, self).save(*args, **kwargs)


if 'django.contrib.auth' in settings.INSTALLED_APPS:
    import uuid
    from django.conf import settings
    from django.contrib.auth.models import User
    
    class ApiKey(models.Model):
        user = models.OneToOneField(User, related_name='api_key')
        key = models.CharField(max_length=256, blank=True, default='')
        created = models.DateTimeField(default=datetime.datetime.now)
        
        def save(self, *args, **kwargs):
            if not self.key:
                self.key = self.generate_key()
            
            return super(ApiKey, self).save(*args, **kwargs)
        
        def generate_key(self):
            # Get a random UUID.
            new_uuid = uuid.uuid4()
            # Hmac that beast.
            return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()
    
    
    def create_api_key(sender, **kwargs):
        if kwargs.get('created') is True:
            ApiKey.objects.create(user=kwargs.get('instance'))
    
    models.signals.post_save.connect(create_api_key, sender=User)
