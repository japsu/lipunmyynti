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
EXIT_URL = "http://2010.tracon.fi"

class Phase(object):
    name = "XXX_fill_me_in"
    friendly_name = "XXX Fill Me In"
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
    
            if self.validate(request, form):
                self.save(request, form)
                mark_as_completed(request, self.name)

                # The "Next" button should only proceed with valid data.
                if action == "next":
                    return self.next(request)

            # The "Previous" button should work regardless of form validity.
            if action == "prev":
                return self.prev(request)

            # "Next" with invalid data falls through.

        # POST with invalid data and GET are handled the same.
        return self.get(request, form)

    def prerequisites_completed(self, request):
        completed = get_completed(request)

        if not self.prev_phase:
            return True

        return self.prev_phase in completed

    def validate(self, request, form):
        return form.is_valid()

    def get(self, request, form):
        order = get_order(request)

        context = RequestContext(request, {})
        vars = dict(self.vars(request, form), form=form, order=order, phase=self)
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
        clear_completed(request)
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

welcome_view = WelcomePhase()

class TicketsPhase(Phase):
    name = "tickets_phase"
    friendly_name = "Liput"
    template = "ticket_sales/tickets.html"
    prev_phase = "welcome_phase"
    next_phase = "shirts_phase"

    def make_form(self, request):
        order = get_order(request)
        return init_form(ProductInfoForm, request, instance=order.product_info)

    def save(self, request, form):
        order = get_order(request)

        product_info = form.save()

        order.product_info = product_info
        order.save()

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
        ladyfit_sizes, normal_sizes = list(), list()

        for container, ladyfit in ((normal_sizes, False), (ladyfit_sizes, True)):
            for size in self.__get_sizes(ladyfit=ladyfit):
                try:
                    shirt_order = ShirtOrder.objects.get(
                        order=order,
                        size=size
                    )
                    count = shirt_order.count
                except ShirtOrder.DoesNotExist:
                    count = 0

                container.append((size, count))

        return dict(normal_sizes=normal_sizes, ladyfit_sizes=ladyfit_sizes)

    def save(self, request, form):
        order = get_order(request)
        errors = set()
        for size in self.__get_sizes():
            # Some shirt sizes are not available, but they are shown for
            # symmetry.
            available = size.available

            # Try to extract the number of shirts of a size from the POST
            # form data.
            try:
                count = int(request.POST.get("s%d" % size.pk, 0))
            except ValueError:
                errors.add("syntax")
                count = 0

            # Negative amounts of shirts are not tolerated.
            if count < 0:
                errors.add("negative")
                count = 0

            # Ordering shirts of unavailable sizes though POST data
            # manipulation is not tolerated.
            if count > 0 and not available:
                errors.add("hax")
                count = 0

            # Now check if we're modifying an existing order and a shirt
            # order for this size already exists.
            try:
                shirt_order = ShirtOrder.objects.get(
                    order=order,
                    size=size
                )
            except ShirtOrder.DoesNotExist:
                shirt_order = None

            if shirt_order is None and count > 0:
                # Create a new shirt order.
                shirt_order = ShirtOrder(
                    order=order,
                    size=size,
                    count=count
                )
                shirt_order.save()
            elif shirt_order is not None and count > 0:
                # Update an existing shirt order.
                shirt_order.count = count
                shirt_order.save()
            elif shirt_order is not None and count == 0:
                # This shirt order was zeroed, so delete it.
                shirt_order.delete()
     
            # do nothing on shirt_order None and count 0
            # TODO: Communicate errors to template and re-do phase

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
    prev_phase = "shirts_phase"
    next_phase = "thanks_phase"

    def vars(self, request, form):
        order = get_order(request)
        shirts = ShirtOrder.objects.filter(order=order)

        return dict(shirts=shirts)

    def save(self, request, form):
        order = get_order(request)
        order.confirm()
        order.save()

confirm_view = ConfirmPhase()

class ThanksPhase(Phase):
    name = "thanks_phase"
    friendly_name = "Kuitti"
    template = "ticket_sales/thanks.html"
    prev_phase = None
    next_phase = None
    methods = ["GET"]

    def vars(self, request, form):
        order = get_order(request)
        shirts = ShirtOrder.objects.filter(order=order)

        return dict(shirts=shirts)

thanks_view = ThanksPhase()

ALL_PHASES = [welcome_view, tickets_view, shirts_view, address_view, confirm_view, thanks_view]
