# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template
from django.core.urlresolvers import reverse

from tracon.ticket_sales.views import ALL_PHASES

register = template.Library()

@register.simple_tag
def url_ptr(name):
    return reverse(name)
