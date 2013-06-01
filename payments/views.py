# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.contrib.messages import add_message, INFO, ERROR, WARNING
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from ticket_sales.helpers import init_form, get_order

from .forms import PaymentForm

# http://demo1.checkout.fi/xml2.php

# XXX where should this be defined?
class PaymentStatus:
  TIMEOUT = -3
  ABORTED = -2
  CANCELLED = -1

  OK = 2
  DELAYED = 3
  FROZEN = 6

  CANCELLED_STATUSES = [TIMEOUT, ABORTED, CANCELLED]

@require_GET
def payment_view(request):
  order = get_order(request)
  if not order.customer:
    add_message(request, ERROR, "Yritetty maksaa keskeneräinen tilaus. This shouldn't happen.")
    return redirect('welcome_phase')

  try:
    payment_info = PaymentForm(request.GET).save()
  except ValueError:
    add_message(request, ERROR, 'Maksu epäonnistui. Ole hyvä ja ota yhteyttä: {0}'
      .format(settings.DEFAULT_FROM_EMAIL))
    return redirect('confirm_phase')

  if payment_info.STATUS in PaymentStatus.CANCELLED_STATUSES:
    add_message(request, INFO, 'Maksu peruttiin.') # XXX
    return redirect('confirm_phase')

  order.confirm_order(send_email=False)

  if payment_info.STATUS == PaymentStatus.OK:
    order.confirm_payment() # send_email=True
    return redirect('thanks_phase')
  else:
    add_message(request, WARNING, 'Tilauksesi onnistui, mutta emme saaneet lopullista vahvistusta maksustasi. Saat erillisen maksuvahvistusviestin, kun maksusi on vahvistettu.')
    return redirect('thanks_phase')

def make_form(request):
  return init_form(PaymentForm, request, instance=None)
