import urllib

from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate
from django.core.urlresolvers import reverse
from django.shortcuts import render


def login(request):
    """ First step of process, redirects user to facebook, which redirects to authentication_callback. """

    args = {
        'client_id': settings.FACEBOOK_APP_ID,
        'scope': settings.FACEBOOK_SCOPE,
        'redirect_uri': request.build_absolute_uri(reverse('facebook-authenticaton-callback')),
    }
    return HttpResponseRedirect('https://www.facebook.com/dialog/oauth?%s' % urllib.urlencode(args))


def authentication_callback(request):
    """ Second step of the login process.
    It reads in a code from Facebook, then redirects back to the home page. """
    code = request.GET.get('code')
    user = authenticate(token=code, request=request)

    if user:
        auth_login(request, user)

        #figure out where to go after setup
        url = settings.LOGIN_REDIRECT_URL or '/'
        resp = HttpResponseRedirect(url)
    else:
        resp = render(request, 'error.html')
    
    return resp
