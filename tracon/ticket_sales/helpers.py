# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from tracon.ticket_sales.models import Order, ShirtOrder, OrderProduct

__all__ = [
    "redirect",
    "set_order",
    "get_order",
    "clear_order",
    "destroy_order",
    "init_form",
]

ORDER_KEY = "tracon.ticket_sales.order_id"
PRIOR_KEY = "tracon.ticket_sales.prior_orders"

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
    
    order.order_product_set.all().delete()
    order.shirt_order_set.all().delete()

    if order.customer:
        order.customer.delete()

    order.delete()
    clear_order(request)

def init_form(form_class, request, instance=None, prefix=None):
    if request.method == "POST":
        return form_class(request.POST, request.FILES, instance=instance, prefix=prefix)
    else:
        return form_class(instance=instance, prefix=prefix)
