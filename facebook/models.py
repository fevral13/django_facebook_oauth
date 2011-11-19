import urllib

from django.db import models
from django.contrib.auth.models import User
try:
    from simplejson import loads
except ImportError:
    # fallback to existing, though slow implementation
    from django.utils.simplejson import loads



class FacebookProfile(models.Model):
    user = models.OneToOneField(User)
    facebook_id = models.BigIntegerField()
    access_token = models.CharField(max_length=150)

    def get_facebook_profile(self):
        fb_profile = urllib.urlopen('https://graph.facebook.com/me?access_token=%s' % self.access_token)
        return loads(fb_profile)
