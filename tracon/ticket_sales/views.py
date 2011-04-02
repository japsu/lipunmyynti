# encoding: utf-8
# vim: shiftwidth=4 expandtab

from reportlab.pdfgen import canvas

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from tracon.ticket_sales.models import *
from tracon.ticket_sales.forms import *
from tracon.ticket_sales.helpers import *
from tracon.ticket_sales.utils import *
from tracon.ticket_sales.format import *

__all__ = [
    "welcome_view",
    "tickets_view",
    "address_view",
    "confirm_view",
    "thanks_view",
    "ALL_PHASES",
    "manage_view",
    "stats_view",
    "payments_view",
    "process_single_payment_view",
    "confirm_single_payment_view",
    "process_multiple_payments_view",
    "confirm_multiple_payments_view",
    "create_batch_view",
    "render_batch_view",
    "cancel_batch_view",
    "deliver_batch_view",
    "search_view",
    "closed_view",
]    

FIRST_PHASE = "welcome_phase"
LAST_PHASE = "thanks_phase"
EXIT_URL = "http://2011.tracon.fi"

def multiform_validate(forms):
    return ["syntax"] if not all(
        i.is_valid() and (i.instance.target.available or i.cleaned_data["count"] == 0)
        for i in forms
    ) else []

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
        return not order.is_confirmed

    def validate(self, request, form):
        if not form.is_valid():
            return ["syntax"]
        else:
            return []

    def get(self, request, form, errors):
        order = get_order(request)

        context = RequestContext(request, {})
        phases = []

        for phase in ALL_PHASES:
            available = phase.index < self.index and not order.is_confirmed
            current = phase is self

            phases.append((phase, available, current))

        vars = dict(self.vars(request, form), form=form, errors=errors, order=order, phase=self, phases=phases)
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

    def save(self, request, form):
        order = get_order(request)
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
    next_phase = "address_phase"

    def make_form(self, request):
        order = get_order(request)
        forms = []

        # XXX When the admin changes the available property of products, existing sessions in the Tickets phase will break.
        for product in Product.objects.filter(available=True).order_by("id"):
            order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)
            form = init_form(OrderProductForm, request, instance=order_product, prefix="o%d" % order_product.pk)
            forms.append(form)

        return forms

    def validate(self, request, form):
        errors = multiform_validate(form)

        # If the above step failed, not all forms have cleaned_data.
        if errors:
            return errors

        if sum(i.cleaned_data["count"] for i in form) <= 0:
            errors.append("zero")
            return errors

        if (is_soldout(dict((i.instance.product, i.cleaned_data["count"]) for i in form))):
            errors.append("soldout")
            return errors

        return []

    def save(self, request, form):
        multiform_save(form)

tickets_view = TicketsPhase()

class AddressPhase(Phase):
    name = "address_phase"
    friendly_name = "Toimitusosoite"
    template = "ticket_sales/address.html"
    prev_phase = "tickets_phase"
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
    friendly_name = "Vahvistaminen"
    template = "ticket_sales/confirm.html"
    prev_phase = "address_phase"
    next_phase = "thanks_phase"
    next_text = "Vahvista &#10003;"

    def validate(self, request, form):
        order = get_order(request)
        if (is_soldout(dict((i.product, i.count) for i in order.product))):
            errors.append("soldout_confirm")
            return errors
        return [] 

    def vars(self, request, form):
        order = get_order(request)
        products = OrderProduct.objects.filter(order=order, count__gt=0)

        return dict(products=products)

    def save(self, request, form):
        pass

    def next(self, request):
        order = get_order(request)

        # .confirm_* call .save
        order.confirm_order()
        
        return super(ConfirmPhase, self).next(request)

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
        products = OrderProduct.objects.filter(order=order)

        return dict(products=products)

    def save(self, request, form):
        pass

    def next(self, request):
        # Start a new order
        clear_order(request)

        return redirect(self.next_phase)

class ClosedPhase(Phase):
    name = "welcome_phase"
    friendly_name = "Tervetuloa!"
    template = "ticket_sales/closed.html"
    prev_phase = None
    next_phase = None
    can_cancel = True
    index = 0

    def available(self, request):
        return True

    def save(self, request, form):
        pass

    def next(self, request):
        return HttpResponseRedirect("http://2011.tracon.fi")

thanks_view = ThanksPhase()
closed_view = ClosedPhase()

ALL_PHASES = [welcome_view, tickets_view, address_view, confirm_view, thanks_view]
for num, phase in enumerate(ALL_PHASES):
    phase.index = num

@login_required
def manage_view(request):
    batches = Batch.objects.all()

    vars = dict(batches=batches)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/manage.html", vars, context_instance=context)

@login_required
def stats_view(request):
    # TODO rewrite me
    vars = {}
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/stats.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_payments")
@require_GET
def payments_view(request):
    vars = dict(
        single_form=SinglePaymentForm(),
        multiple_form=MultiplePaymentsForm()
    )
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/payments.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_payments")
@require_POST
def process_single_payment_view(request):
    form = SinglePaymentForm(request.POST)
    if not form.is_valid():
        return admin_error_page(request, u"Tarkista syöte.")    

    try:
        order = get_order_by_ref(form.cleaned_data["ref_number"])
    except Order.DoesNotExist:
        return admin_error_page(request, u"Annetulla viitenumerolla ei löydy tilausta.")
    if not order.is_confirmed:
        return admin_error_page(request, u"Viitenumeroa vastaavaa tilausta ei ole vahvistettu.")
    if order.is_paid:
        return admin_error_page(request, u"Tilaus on jo merkitty maksetuksi %s." % format_date(order.payment_date))

    vars = dict(order=order)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/review_single.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_payments")
@require_POST
def confirm_single_payment_view(request):
    form = ConfirmSinglePaymentForm(request.POST)
    if not form.is_valid():
        return admin_error_page(request, u"Jotain hämärää yritetty!")

    order = get_object_or_404(Order, id=form.cleaned_data["order_id"])
    order.confirm_payment(date.today())

    vars = dict(order=order)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/single_payment_ok.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_payments")
@require_POST
def process_multiple_payments_view(request):
    form = MultiplePaymentsForm(request.POST)
    if not form.is_valid():
        return admin_error_page(request, u"Älä pliis jätä sitä pastee tähän -kenttää tyhjäks.")

    dump = form.cleaned_data["dump"]
    lines = dump.split("\n")
    payments = list(parse_payments(lines))

    vars = dict(payments=payments, dump=dump)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/review_multiple.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_payments")
@require_POST
def confirm_multiple_payments_view(request):
    form = MultiplePaymentsForm(request.POST)
    if not form.is_valid():
        return admin_error_page(request, u"Jotain hämärää yritetty!")

    dump = form.cleaned_data["dump"]
    lines = dump.split("\n")
    payments = list(parse_payments(lines))

    for line, result, date, order in payments:
        if result == ParseResult.OK:
            order.confirm_payment(date)

    vars = dict(payments=payments)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/multiple_payments_ok.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_batches")
@require_http_methods(["POST", "GET"])
def create_batch_view(request):
    if request.method == "POST":
        form = CreateBatchForm(request.POST)
        if form.is_valid():
            batch = Batch.create(max_orders=form.cleaned_data["max_orders"])

            vars = dict(batch=batch)
            context = RequestContext(request, {})
            return render_to_response("ticket_admin/create_batch_ok.html", vars, context_instance=context)
    else:
        form = CreateBatchForm()

    vars = dict(form=form)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/create_batch.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_batches")
@require_GET
def render_batch_view(request, batch_id):
    batch = get_object_or_404(Batch, id=int(batch_id))

    response = HttpResponse(mimetype="application/pdf")
    response["Content-Disposition"] = 'filename=batch%03d.pdf' % batch.id
    c = canvas.Canvas(response)
    batch.render(c)
    c.save()

    return response

@permission_required("ticket_sales.can_manage_batches")
@require_http_methods(["POST", "GET"])
def cancel_batch_view(request, batch_id):
    batch = get_object_or_404(Batch, id=int(batch_id))

    if request.method == "POST":
        batch.cancel()

        vars = dict()
        context = RequestContext(request, {})
        return render_to_response("ticket_admin/cancel_batch_ok.html", vars, context_instance=context)

    else:
        vars = dict(batch=batch)
        context = RequestContext(request, {})
        return render_to_response("ticket_admin/cancel_batch.html", vars, context_instance=context)

@permission_required("ticket_sales.can_manage_batches")
@require_http_methods(["POST", "GET"])
def deliver_batch_view(request, batch_id):
    batch = get_object_or_404(Batch, id=int(batch_id))

    if batch.is_delivered:
        return admin_error_page(request, "Already delivered")

    vars = dict(batch=batch)
    context = RequestContext(request, {})

    if request.method == "POST":
        batch.confirm_delivery()

        return render_to_response("ticket_admin/deliver_batch_ok.html", vars, context_instance=context)

    else:
        return render_to_response("ticket_admin/deliver_batch.html", vars, context_instance=context)

# XXX Wrong perm
@permission_required("ticket_sales.can_manage_batches")
@require_http_methods(["GET","POST"])
def search_view(request):
    orders = []

    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            orders = perform_search(**form.cleaned_data)
    else:
        form = SearchForm()
        
    vars = dict(form=form, orders=orders)
    context = RequestContext(request, {})

    return render_to_response("ticket_admin/search.html", vars, context_instance=context)

def admin_error_page(request, error):
    vars = dict(error=error)
    context = RequestContext(request, {})
    return render_to_response("ticket_admin/error.html", vars, context_instance=context)
