# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def url_ptr(name):
    return reverse(name)

@register.simple_tag
def render_order_compact(order):
    return render_to_string("ticket_admin/compact_order.html", dict(order=order))
