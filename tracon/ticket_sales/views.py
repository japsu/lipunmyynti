# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template import RequestContext

from tracon.ticket_sales.models import *
from tracon.ticket_sales.forms import *

def welcome_view(request):
    if request.method == "GET":
        form = WelcomeForm()

        vars = RequestContext(request, {"form" : form})
        return render_to_response("ticket_sales/welcome.html", vars)
    elif request.method == "POST":
        form = WelcomeForm(request.POST)

        order = Order(ip_address = request.META["REMOTE_ADDR"])
        order.save()

        request.session["tracon.ticket_sales.order_id"] = order.pk

        return HttpResponseRedirect(reverse("tickets_view"))
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def tickets_view(request):
    return render_to_response("ticket_sales/tickets.html", {})

def shirts_view(request):
    return render_to_response("ticket_sales/shirts.html", {})

def address_view(request):
    return render_to_response("ticket_sales/address.html", {})

def confirm_view(request):
    return render_to_response("ticket_sales/confirm.html", {})

def thanks_view(request):
    return render_to_response("ticket_sales/thanks.html", {})

