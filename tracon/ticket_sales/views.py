# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from tracon.ticket_sales.models import *
from tracon.ticket_sales.forms import *

def welcome_view(request):
    if request.method == "GET":
        vars = RequestContext(request, {})
        return render_to_response("ticket_sales/welcome.html", vars)
    elif request.method == "POST":
        if not request.session.has_key("tracon.ticket_sales.order_id"):
            order = Order(ip_address = request.META["REMOTE_ADDR"])
            order.save()

            request.session["tracon.ticket_sales.order_id"] = order.pk

        request.session["tracon.ticket_sales.completed"] = ["welcome"]
        return HttpResponseRedirect(reverse("tickets_view"))
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def tickets_view(request):
    if not "welcome" in request.session.get("tracon.ticket_sales.completed", []):
        return HttpResponseRedirect(reverse("welcome_view"))

    order = Order.objects.get(
        pk=request.session["tracon.ticket_sales.order_id"])

    if request.method == "GET":
        form = ProductInfoForm(instance=order.product_info)

        vars = RequestContext(request, {"form" : form})
        return render_to_response("ticket_sales/tickets.html", vars)

    elif request.method == "POST":
        form = ProductInfoForm(request.POST, instance=order.product_info)

        try:
            product_info = form.save()
        except ValueError:
            vars = RequestContext(request, {"form" : form})
            return render_to_response("ticket_sales/tickets.html", vars)

        order.product_info = product_info
        order.save()

        request.session.get("tracon.ticket_sales.completed").append("tickets")
        return HttpResponseRedirect(reverse("shirts_view"))

    else:
        return HttpResponseNotAllowed(["GET", "POST"])        

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
        )
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
