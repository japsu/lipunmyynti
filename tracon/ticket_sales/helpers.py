# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from tracon.ticket_sales.models import Order

__all__ = [
    "redirect",
    "set_order",
    "get_order",
    "clear_order",
    "destroy_order",
    "get_completed",
    "mark_as_completed",
    "clear_completed",
    "init_form",
]

ORDER_KEY = "tracon.ticket_sales.order_id"
COMPLETED_KEY = "tracon.ticket_sales.completed_phases"

def redirect(view_name, **kwargs):
    return HttpResponseRedirect(reverse(view_name, kwargs=kwargs))

def set_order(request, order):
    request.session[ORDER_KEY] = order.pk

def get_order(request):
    order_id = request.session.get(ORDER_KEY, None)
    if order_id is not None:
        return Order.objects.get(id=order_id)
    else:
        o = Order.objects.create()
        set_order(request, o)
        return o

def clear_order(request):
    if request.session.has_key(ORDER_KEY):
        del request.session[ORDER_KEY]

def destroy_order(request):
    order = get_order(request)
    
    if order.product_info:
        order.product_info.delete()

    for shirt in ShirtOrder.objects.get(order=order):
        shirt.delete()

    order.delete()
    clear_order(request)

def get_completed(request):
    return request.session.get(COMPLETED_KEY, [])

def mark_as_completed(request, phase_name):
    completed = get_completed(request)
    completed.append(phase_name)
    request.session[COMPLETED_KEY] = completed

def clear_completed(request):
    if request.session.has_key(COMPLETED_KEY):
        del request.session[COMPLETED_KEY]

def init_form(form_class, request, instance=None):
    if request.method == "POST":
        args = [request.POST]
    else:
        args = []

    if instance is not None:
        kwargs = dict(instance=instance)
    else:
        kwargs = {}

    return form_class(*args, **kwargs)
