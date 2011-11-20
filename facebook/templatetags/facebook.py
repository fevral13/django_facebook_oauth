# -*- coding:utf-8 -*-
from django.template import Library
from django.template.loader import render_to_string


register = Library()

@register.simple_tag(takes_context=True)
def facebook_button(context):
    return render_to_string('facebook-button.html', context)
