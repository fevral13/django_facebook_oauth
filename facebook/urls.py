# -*- coding:utf-8 -*-
from django.conf.urls.defaults import url, patterns



urlpatterns = patterns('facebook.views',
    url(r'^login/$', 'login', name='facebook-login'),
    url(r'^authentication_callback/$', 'authentication_callback', name='facebook-authenticaton-callback'),
)
