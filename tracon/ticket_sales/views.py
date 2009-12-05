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
    "thanks_view",
    "ALL_PHASES"
]    

FIRST_PHASE = "welcome_phase"
LAST_PHASE = "thanks_phase"
EXIT_URL = "http://2010.tracon.fi"

def multiform_validate(forms):
    return [] if all(i.is_valid() for i in forms) else ["syntax"]

def multiform_save(forms):
    return [i.save() for i in forms]

class Phase(object):
    name = "XXX_fill_me_in"
    friendly_name = "XXX Fill Me In"
    methods = ["GET", "POST"]
    template = "ticket_sales/dummy.html"
    prev_phase = None
    next_phase = None
    next_text = "Seuraava &raquo;"
    can_cancel = True
    index = None

    def __call__(self, request):
        if request.method not in self.methods:
            return HttpResponseNotAllowed(self.methods)

        form = self.make_form(request)
        
        if request.method == "POST":
            # Which button was clicked?
            action = request.POST.get("action", "cancel")

            # On "Cancel" there's no need to do form validation, just bail out
            # right away.
            if action == "cancel":
                return self.cancel(request)

            if action not in ("next", "prev"):
                # TODO the user is manipulating the POST data
                raise NotImplementedError("evil user")

            # Data validity is checked before even attempting save.
            errors = self.validate(request, form)

            if not errors:    
                self.save(request, form)

                # The "Next" button should only proceed with valid data.
                if action == "next":
                    return self.next(request)

            # The "Previous" button should work regardless of form validity.
            if action == "prev":
                return self.prev(request)

            # "Next" with invalid data falls through.
        else:
            errors = []

        # POST with invalid data and GET are handled the same.
        return self.get(request, form, errors)

    def validate(self, request, form):
        if not form.is_valid():
            return ["syntax"]
        else:
            return []

    def get(self, request, form, errors):
        order = get_order(request)

        context = RequestContext(request, {})
        vars = dict(self.vars(request, form), form=form, errors=errors, order=order, phase=self)
        return render_to_response(self.template, vars, context_instance=context)

    def make_form(self, request):
        return init_form(NullForm, request, instance=None)

    def save(self, request, form):
        form.save()

    def next(self, request):
        return redirect(self.next_phase)

    def prev(self, request):
        return redirect(self.prev_phase)

    def cancel(self, request):
        destroy_order(request)
        return HttpResponseRedirect(EXIT_URL)

    def vars(self, request, form):
        return {}

class WelcomePhase(Phase):
    name = "welcome_phase"
    friendly_name = "Tervetuloa"
    template = "ticket_sales/welcome.html"
    prev_phase = None
    next_phase = "tickets_phase"

    def make_form(self, request):
        order = get_order(request)
        return init_form(WelcomeForm, request, instance=order)

    def save(self, request, form):
        order = form.save()
        order.ip_address = request.META.get("REMOTE_ADDR")
        order.save()

        set_order(request, order)

    def available(self, request):
        order = get_order(request)
        return not order.is_confirmed

welcome_view = WelcomePhase()

class TicketsPhase(Phase):
    name = "tickets_phase"
    friendly_name = "Liput"
    template = "ticket_sales/tickets.html"
    prev_phase = "welcome_phase"
    next_phase = "shirts_phase"

    def make_form(self, request):
        order = get_order(request)
        forms = []

        for product in Product.objects.order_by("id"):
            order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)
            form = init_form(OrderProductForm, request, instance=order_product, prefix="o%d" % order_product.pk)
            forms.append(form)

        return forms

    def validate(self, request, form):
        return multiform_validate(form)

    def save(self, request, form):
        multiform_save(form)

    def next(self, request):
        order = get_order(request)

        if order.tshirts > 0:
            # The user is ordering T-shirts. Ask for shirt sizes.
            next_phase = "shirts_phase"
        else:
            # The user is not ordering T-shirts. Skip the shirt size phase.
            next_phase = "address_phase"

        return redirect(next_phase)

tickets_view = TicketsPhase()

class ShirtsPhase(Phase):
    name = "shirts_phase"
    friendly_name = "Paidat"
    template = "ticket_sales/shirts.html"
    next_phase = "address_phase"
    prev_phase = "tickets_phase"

    def __get_sizes(self, **kwargs):
        return ShirtSize.objects.filter(**kwargs).order_by("id")

    def vars(self, request, form):
        order = get_order(request)
        num_shirts = order.tshirts
        ladyfit_hack = [(False, "Tavallinen paita"), (True, "Ladyfit-paita")]
        return dict(num_shirts=num_shirts, ladyfit_hack=ladyfit_hack)

    def make_form(self, request):
        order = get_order(request)
        sizes = self.__get_sizes()
        forms = []
        
        for size in sizes:
            shirt_order, created = ShirtOrder.objects.get_or_create(order=order, size=size)
            form = init_form(ShirtOrderForm, request, instance=shirt_order, prefix="s%d" % shirt_order.pk)
            forms.append(form)

        return forms

    def validate(self, request, form):
        return multiform_validate(form)

    def save(self, request, form):
        multiform_save(form)

    def available(self, request):
        order = get_order(request)
        sup_available = super(ShirtsPhase, self).available(request)

        if not sup_available:
            return False

        return order.tshirts > 0

shirts_view = ShirtsPhase()

class AddressPhase(Phase):
    name = "address_phase"
    friendly_name = "Toimitusosoite"
    template = "ticket_sales/address.html"
    prev_phase = "shirts_phase"
    next_phase = "confirm_phase"

    def make_form(self, request):
        order = get_order(request)

        return init_form(CustomerForm, request, instance=order.customer)

    def prev(self, request):
        order = get_order(request)

        if order.tshirts:
            return redirect("shirts_phase")
        else:
            return redirect("tickets_phase")

    def save(self, request, form):
        order = get_order(request)
        cust = form.save()

        order.customer = cust
        order.save()

address_view = AddressPhase()

class ConfirmPhase(Phase):
    name = "confirm_phase"
    friendly_name = "Tilausvahvistus"
    template = "ticket_sales/confirm.html"
    prev_phase = "address_phase"
    next_phase = "thanks_phase"
    next_text = "Vahvista &#10003;"

    def vars(self, request, form):
        order = get_order(request)
        shirts = ShirtOrder.objects.filter(order=order, count__gt=0)
        products = OrderProduct.objects.filter(order=order, count__gt=0)

        return dict(shirts=shirts, products=products)

    def save(self, request, form):
        order = get_order(request)
        order.confirm()
        order.save()

confirm_view = ConfirmPhase()

class ThanksPhase(Phase):
    name = "thanks_phase"
    friendly_name = "Kiitos!"
    template = "ticket_sales/thanks.html"
    prev_phase = None
    next_phase = "welcome_phase"
    next_text = "Uusi tilaus"
    can_cancel = False

    def available(self, request):
        order = get_order(request)
        return order.is_confirmed

    def vars(self, request, form):
        order = get_order(request)
        shirts = ShirtOrder.objects.filter(order=order)
        products = OrderProduct.objects.filter(order=order)

        return dict(shirts=shirts, products=products)

    def save(self, request, form):
        pass

    def next(self, request):
        # Start a new order
        clear_order(request)

        return redirect(self.next_phase)

thanks_view = ThanksPhase()

ALL_PHASES = [welcome_view, tickets_view, shirts_view, address_view, confirm_view, thanks_view]
for num, phase in enumerate(ALL_PHASES):
    phase.index = num
