# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from payments.models import *
from payments.forms import *
from ticket_sales.helpers import *

# Create your views here.
# http://demo1.checkout.fi/xml2.php

def payment_view(request):
  password = "SAIPPUAKAUPPIAS"
  version = "0001"
  if request.method == "GET":
    form = PaymentForm(request.GET)
    if form.is_valid():
      payment_info = form.save()
      # MAC on oikein jos ei palauta virhettä
      if payment_info.check_mac() == None:
        # Onko tälle parempaa paikkaa?
        request.session['payment_status'] = payment_info.STATUS
        # Maksu meni läpi jos STATUS = 2
        return HttpResponseRedirect('/vahvistus/')
      else:
       return HttpResponse(payment_info.check_mac())
    # Testausfunktion
    elif request.GET.get('test') == '1':
      request.session['payment_status'] = 2
      return HttpResponseRedirect('/vahvistus/')
    else:
      return HttpResponse("Ready: %s "%str("error"))
  else:
    return HttpResponse("Ready: %s "%str("not GET"))

def make_form(request):
  return init_form(PaymentForm, request, instance=None)
