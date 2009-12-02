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
PRODUCT_NAMES = ("tickets", "tickets_tshirts", "tickets_tshirts_accommodation", "tickets_accommodation")

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

        # Check phase proconditions
        order = get_order(request)
        if not self.available(request):
            if order.is_confirmed:
                return redirect(LAST_PHASE)
            else:
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

            # Data validity is checked before even attempting save.
            errors = self.validate(request, form)

            if not errors:    
                self.save(request, form)

                set_completed(request, self.index)

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

    def available(self, request):
        order = get_order(request)
        completed = get_completed(request)

        return self.index <= completed + 1 and not order.is_confirmed

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

        for product in Product.objects.order_by("id"):
            OrderProduct.objects.get_or_create(
                order=order,
                product=product
            )

        queryset = OrderProduct.objects.filter(order=order)
        formset = init_formset(OrderProductFormset, request, queryset=queryset)

        # XXX I feel dirty returning a formset instead of a form.
        return formset

    def save(self, request, form):
        # It's actually a formset.
        formset = form

        # There's no point in leaving OrderProducts with count=0 lying around.
        for order_product in formset.save(commit=False):
            if order_product.count > 0:
                order_product.save()
            else:
                order_product.delete()

    def next(self, request):
        order = get_order(request)

        if order.tshirts > 0:
            # The user is ordering T-shirts. Ask for shirt sizes.
            set_completed(request, self.index)
            next_phase = "shirts_phase"
        else:
            # The user is not ordering T-shirts. Skip the shirt size phase.
            set_completed(request, shirts_phase.index)
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

    def __get_count(self, request, size):
        # Try to extract the number of shirts of a size from the POST
        # form data.
        data = int(request.POST.get("s%d" % size.pk, None))
        if data is None:
            return 0

        try:
            return int(data)
        except ValueError:
            raise

    def vars(self, request, form):
        order = get_order(request)
        ladyfit_sizes, normal_sizes = list(), list()
        num_shirts = order.tshirts

        for container, ladyfit in ((normal_sizes, False), (ladyfit_sizes, True)):
            for size in self.__get_sizes(ladyfit=ladyfit):
                # TODO Retain user input even if it's faulty

                try:
                    shirt_order = ShirtOrder.objects.get(
                        order=order,
                        size=size
                    )
                    count = shirt_order.count
                except ShirtOrder.DoesNotExist:
                    count = 0

                container.append((size, count))

        return dict(normal_sizes=normal_sizes, ladyfit_sizes=ladyfit_sizes, num_shirts=num_shirts)

    def validate(self, request, form):
        order = get_order(request)
        errors = set()

        num_shirts = 0

        for size in self.__get_sizes():
            # Some shirt sizes are not available, but they are shown for
            # symmetry.
            available = size.available

            try:
                count = self.__get_count(request, size)
            except ValueError:
                # Non-integral data                
                errors.add("syntax")

            if count < 0:
                # Negative amounts of shirts are not tolerated.
                errors.add("negative")
                continue
            elif count > 0 and not available:
                # Ordering shirts of unavailable sizes though POST data
                # manipulation is not tolerated.
                errors.add("hax")
                continue

            num_shirts += count

        # Make sure the number of shirt ordered matches the number of ticket
        # products that include a shirt.
        if num_shirts != order.tshirts:
            errors.add("num_shirts")

        return list(errors)

    def save(self, request, form):
        order = get_order(request)
        for size in self.__get_sizes():
            count = self.__get_count(request, size)

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
        shirts = ShirtOrder.objects.filter(order=order)

        return dict(shirts=shirts)

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

        return dict(shirts=shirts)

    def save(self, request, form):
        pass

    def next(self, request):
        # Start a new order
        clear_order(request)
        clear_completed(request)

        return redirect(self.next_phase)

thanks_view = ThanksPhase()

ALL_PHASES = [welcome_view, tickets_view, shirts_view, address_view, confirm_view, thanks_view]
for num, phase in enumerate(ALL_PHASES):
    phase.index = num

def redirect_view(self, request):
    completed = get_completed(request)
    next = completed + 1
    view = ALL_PHASES[next]
    return redirect(view.name)
