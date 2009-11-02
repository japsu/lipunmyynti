# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from tracon.ticket_sales.models import *
from tracon.ticket_sales.forms import *
from tracon.ticket_sales.helpers import *

__all__ = [
    "welcome_view",
    "tickets_view",
    "shirts_view",
    "address_view",
    "confirm_view",
    "thanks_view"
]    

FIRST_PHASE = "welcome_phase"
EXIT_URL = "http://2010.tracon.fi"

class Phase(object):
    name = "XXX_fill_me_in"
    methods = ["GET", "POST"]
    template = "ticket_sales/dummy.html"
    prev_phase = None
    next_phase = None

    def __call__(self, request):
        if request.method not in self.methods:
            return HttpResponseNotAllowed(self.methods)

        if not self.prerequisites_completed(request):
            return redirect(FIRST_PHASE)

        form = self.make_form(request)
        
        if request.method == "GET":
            return self.get(request, form)
        elif request.method == "POST":
            self.save(request, form)
            mark_as_completed(request, self.name)

            action = request.POST.get("action", "next")
            if action in ("next", "prev", "cancel"):
                method = getattr(self, action)
                return method(request)

    def prerequisites_completed(self, request):
        completed = get_completed(request)

        if not self.prev_phase:
            return True

        return self.prev_phase in completed

    def get(self, request, form):
        order = get_order(request)

        context = RequestContext(request, {})
        vars = dict(form=form, order=order, phase=self)
        return render_to_response(self.template, vars, context_instance=context)

    def make_form(self, request):
        return NullForm(request.POST)

    def save(self, request, form):
        form.save()

    def next(self, request):
        return redirect(self.next_phase)

    def prev(self, request):
        return redirect(self.prev_phase)

    def cancel(self, request):
        destroy_order(request)
        clear_completed(request)
        return HttpResponseRedirect(EXIT_URL)

class WelcomePhase(Phase):
    name = "welcome_phase"
    template = "ticket_sales/welcome.html"
    prev_phase = None
    next_phase = "tickets_phase"

    def make_form(self, request):
        order = get_order(request)
        return WelcomeForm(request.POST, instance=order, initial=dict(ip_address="0.0.0.0"))

    def save(self, request, form):
        order = form.save()
        order.ip_address = request.META.get("REMOTE_ADDR")
        order.save()

        set_order(request, order)

welcome_view = WelcomePhase()

class TicketsPhase(Phase):
    name = "tickets_phase"
    template = "ticket_sales/tickets.html"
    prev_phase = "welcome_phase"
    next_phase = "shirts_phase"

    def make_form(self, request):
        order = get_order(request)
        return ProductInfoForm(request.POST, instance=order.product_info)

    def save(self, request, form):
        order = get_order(request)

        product_info = form.save()

        order.product_info = product_info
        order.save()

tickets_view = TicketsPhase()

def shirts_view(request):
    if not "tickets" in request.session.get("tracon.ticket_sales.completed", []):
        return HttpResponseRedirect(reverse("welcome_view"))

    sizes = ShirtSize.objects.all()
    order = Order.objects.get(
        pk=request.session["tracon.ticket_sales.order_id"])
    num_shirts = order.product_info.num_shirts

    if request.method == "GET":
        data = []

        for size in sizes:
            try:
                shirt_order = ShirtOrder.objects.get(
                    order=order,
                    size=size
                )
                count = shirt_order.count
            except ShirtOrder.DoesNotExist:
                count = 0

            available = size.available
            data.append((size, count, available))

        vars = RequestContext(request, {"data":data,"num_shirts":num_shirts})
        return render_to_response("ticket_sales/shirts.html")

    elif request.method == "POST":
        data = []
        errors = set()
        for size in sizes:
            available = size.available

            try:
                count = int(request.POST.get("s%d" % size.pk, 0))
            except ValueError:
                errors.add("syntax")
                count = 0

            if count < 0:
                errors.add("negative")
                count = 0

            if count > 0 and not available:
                errors.add("hax")
                count = 0

            try:
                shirt_order = ShirtOrder.objects.get(
                    order=order,
                    size=size
                )
            except ShirtOrder.DoesNotExist:
                shirt_order = None

            if shirt_order is None and count > 0:
                shirt_order = ShirtOrder(
                    order=order,
                    size=size,
                    count=count
                )
                shirt_order.save()
            elif shirt_order is not None and count > 0:
                shirt_order.count = count
                shirt_order.save()
            elif shirt_order is not None and count == 0:
                shirt_order.delete()
     
            # do nothing on shirt_order None and count 0
            data.append((size, count, available))            

        if errors:
            vars = RequestContext(request, {"errors":errors,"data":data,"num_shirts":num_shirts})
            return render_to_response("ticket_sales/shirts.html", vars)
        else:
            request.session["tracon.ticket_sales.completed"].append("shirts")
            return HttpResponseRedirect(reverse("address_view"))

    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def address_view(request):
    if not "shirts" in request.session.get("tracon.ticket_sales.completed", []):
        return HttpResponseRedirect(reverse("welcome_view"))

    order = Order.objects.get(
        pk=request.session["tracon.ticket_sales.order_id"])

    if request.method == "GET":
        form = CustomerForm(instance=order.customer)
    
        vars = RequestContext(request, {"form":form})    
        return render_to_response("ticket_sales/address.html", vars)

    elif request.method == "POST":
        form = CustomerForm(request.POST, instance=order.customer)

        try:
            cust = CustomerForm.save()
        except ValueError():
            vars = RequestContext(request, {"form":form})
            return render_to_response("ticket_saless/address.html", vars)

        order.customer = cust
        order.save()

        request.session["tracon.ticket_sales.completed"].append("address")
        return HttpResponseRedirect(reverse("confirm_view"))

    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def confirm_view(request):
    if not "address" in request.session.get("tracon.ticket_sales.completed", []):
        return HttpResponseRedirect(reverse("welcome_view"))

    order = Order.objects.get(
        pk=request.session["tracon.ticket_sales.order_id"])
    shirts = ShirtOrder.objects.filter(order=order)

    if request.method == "GET":
        vars=RequestContext(request, {
            "order" : order,
            "shirts" : shirts
        })
        return render_to_response("ticket_sales/confirm.html", vars)

    elif request.method == "POST":
        order.confirm()
        order.save()

        del request.session["tracon.ticket_sales.completed"]
        del request.session["tracon.ticket_sales.order_id"]

        request.session["tracon.ticket_sales.thanks_order_id"] = order.pk

        return HttpResponseRedirect(reverse("thanks_view"))

    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def thanks_view(request):
    if request.method == "GET":
        order_id = request.session.get("tracon.ticket_sales.thanks_order_id", None)
        if order_id is None:
            return HttpResponseRedirect(reverse("welcome_view"))

        order = Order.objects.get(pk=order_id)
        shirts = ShirtOrder.objects.filter(order=order)

        vars = RequestContext(request, {"order":order,"shirts":shirts})
        return render_to_response("ticket_sales/thanks.html", vars)
    else:
        return HttpResponseNotAllowed(["GET"])
