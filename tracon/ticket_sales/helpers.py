# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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
        return None

def clear_order(request):
    if request.session.has_key(ORDER_KEY):
        del request.session[ORDER_KEY]

def get_completed(request):
    return request.session.get(COMPLETED_KEY, [])

def mark_as_completed(request, phase_name):
    completed = get_completed(request)
    completed.append(phase_name)
    request.session[COMPLETED_KEY] = completed

def clear_completed(request):
    if request.session.has_key(COMPLETED_KEY):
        del request.session[COMPLETED_KEY]
