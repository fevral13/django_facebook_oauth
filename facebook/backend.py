import urllib
import urlparse

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.db import IntegrityError
try:
    from simplejson import load
except ImportError:
    # fallback to existing, though slow implementation
    from django.utils.simplejson import load

from facebook.models import FacebookProfile



class FacebookBackend:
    def authenticate(self, token=None, request=None):
        """ Reads in a Facebook code and asks Facebook if it's valid and what user it points to. """
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': request.build_absolute_uri(reverse('facebook-authenticaton-callback')),
            'code': token,
        }

        # Get a legit access token
        target = urllib.urlopen('https://graph.facebook.com/oauth/access_token?%s' % urllib.urlencode(args)).read()
        response = urlparse.parse_qs(target)
        access_token = response['access_token'][-1]

        # Read the user's profile information
        fb_profile = urllib.urlopen('https://graph.facebook.com/me?access_token=%s' % access_token)
        fb_profile = load(fb_profile)

        try:
            # Try and find existing user
            fb_user = FacebookProfile.objects.get(facebook_id=fb_profile['id'])
            user = fb_user.user

            # Update access_token
            fb_user.access_token = access_token
            fb_user.save()

        except FacebookProfile.DoesNotExist:
            # No existing user

            # Not all users have usernames
            username = fb_profile.get('username', fb_profile['email'])

            if getattr(settings, 'FACEBOOK_FORCE_SIGNUP', False):
                # No existing user, use anonymous
                user = AnonymousUser()
                user.username = username
                user.first_name = fb_profile['first_name']
                user.last_name = fb_profile['last_name']
                fb_user = FacebookProfile(
                        facebook_id=fb_profile['id'],
                        access_token=access_token
                )
                user.facebookprofile = fb_user

            else:
                # No existing user, create one

                try:
                    user = User.objects.create_user(username, fb_profile['email'])
                except IntegrityError:
                    # Username already exists, make it unique
                    user = User.objects.create_user(username + fb_profile['id'], fb_profile['email'])
                user.first_name = fb_profile['first_name']
                user.last_name = fb_profile['last_name']
                user.save()

                # Create the FacebookProfile
                fb_user = FacebookProfile(user=user, facebook_id=fb_profile['id'], access_token=access_token)
                fb_user.save()

        return user

    def get_user(self, user_id):
        """ Just returns the user of a given ID. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    supports_object_permissions = False
    supports_anonymous_user = True


class UseCurrentUserFacebookBackend(FacebookBackend):
    """
    Behaves similarly to its parent, except that if current user is authenticated, use its instance
    instead of creating new one
    """
    def authenticate(self, token=None, request=None):
        """ Reads in a Facebook code and asks Facebook if it's valid and what user it points to. """
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': request.build_absolute_uri(reverse('facebook-authenticaton-callback')),
            'code': token,
        }

        # Get a legit access token
        target = urllib.urlopen('https://graph.facebook.com/oauth/access_token?%s' % urllib.urlencode(args)).read()
        response = urlparse.parse_qs(target)
        if 'error' in response.keys() or not token:
            return None
        access_token = response['access_token'][-1]

        # Read the user's profile information
        fb_profile = urllib.urlopen('https://graph.facebook.com/me?access_token=%s' % access_token)
        fb_profile = load(fb_profile)

        try:
            # Try and find existing user
            fb_user = FacebookProfile.objects.get(facebook_id=fb_profile['id'])
            user = fb_user.user

            # Update access_token
            fb_user.access_token = access_token

        except FacebookProfile.DoesNotExist:
            if request and request.user.is_authenticated():
                user = request.user
                try:
                    profile = user.facebookprofile
                    # todo: check if this profile contains fb id
                    return user
                except FacebookProfile.DoesNotExist:
                    pass

            else:
                user = User.objects.create_user(fb_profile['email'], fb_profile['email'])
                user.first_name = fb_profile['first_name']
                user.last_name = fb_profile['last_name']
                user.save()

            # Create the FacebookProfile
            fb_user = FacebookProfile(user=user, facebook_id=fb_profile['id'], access_token=access_token)
        fb_user.save()

        return user
