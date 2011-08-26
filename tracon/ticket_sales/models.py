# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models, IntegrityError
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from datetime import time as dtime
from django.core.mail import EmailMessage
from django.conf import settings

from tracon.ticket_sales.format import format_date, format_datetime, format_price
from tracon.receipt.pdf import render_receipt

__all__ = [
    "School",
    "Batch",
    "Product",
    "Customer",
    "Order",
    "OrderProduct",
]

SHIPPING_AND_HANDLING_CENTS = 100
DUE_DAYS = 7
LOW_AVAILABILITY_THRESHOLD = 10

class Batch(models.Model):
    create_time = models.DateTimeField(auto_now=True)
    print_time = models.DateTimeField(null=True, blank=True)
    prepare_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)

    @property
    def is_printed(self):
        return self.print_time is not None

    @property
    def is_prepared(self):
        return self.prepare_time is not None

    @property
    def is_delivered(self):
        return self.delivery_time is not None

    @property
    def delivery_date(self):
        return self.delivery_time.date()

    @property
    def readable_state(self):
        if self.is_delivered:
            return u"Delivered at %s" % format_date(self.delivery_time)
        elif self.is_prepared:
            return u"Prepared at %s; awaiting delivery" % format_date(self.prepare_time)
        elif self.is_printed:
            return u"Printed at %s; awaiting preparation" % format_date(self.print_time)
        else:
            return u"Awaiting print"

    @classmethod
    def create(cls, max_orders=100):
        # XXX concurrency disaster waiting to happen
        # solution: only I do the botching^Wbatching

        batch = cls()
        batch.save()

        orders = Order.objects.filter(
            # Order is confirmed
            confirm_time__isnull=False,

            # Order is paid
            payment_date__isnull=False,

            # Order has not yet been allocated into a Batch
            batch__isnull=True,

            # Order has not been cancelled
            cancellation_time__isnull=True
        ).order_by("confirm_time")

        accepted = 0

        for order in orders:
            # TODO do this in the database
            # Some orders need not be shipped.
            if not order.requires_shipping:
                continue

            order.batch = batch
            order.save()

            accepted += 1
            if accepted >= max_orders:
                break

        return batch

    def render(self, c):
        for order in self.order_set.all():
            order.render(c)

    def cancel(self):
        for order in self.order_set.all():
            order.batch = None
            order.save()

        self.delete()

    def confirm_delivery(self, delivery_time=None):
        if delivery_time is None:
            delivery_time = datetime.now()

        self.delivery_time = delivery_time
        self.save()
        self.send_delivery_confirmation_messages()

    def send_delivery_confirmation_messages(self):
        for order in self.order_set.all():
            order.send_confirmation_message("toimitusvahvistus")

    def __unicode__(self):
        return u"#%d (%s)" % (
            self.pk,
            self.readable_state
        )

    class Meta:
        verbose_name_plural = "batches"

        permissions = (
            ("can_manage_batches", "Can manage batches"),
        )

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    mail_description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=32)
    classname = models.CharField(max_length=32)
    sell_limit = models.IntegerField()
    price_cents = models.IntegerField()
    requires_shipping = models.BooleanField(default=True)
    available = models.BooleanField(default=True)
    ilmoitus_mail = models.CharField(max_length=100)

    @property
    def formatted_price(self):
        return format_price(self.price_cents)
    
    @property
    def in_stock(self):
        return (self.amount_available > 0)

    @property
    def availability_low(self):
        return (self.amount_available < LOW_AVAILABILITY_THRESHOLD)

    @property
    def amount_available(self):
        return self.sell_limit - self.amount_sold

    @property
    def amount_sold(self):
        cnt = OrderProduct.objects.filter(product=self, order__confirm_time__isnull=False, order__cancellation_time__isnull=True).aggregate(models.Sum('count'))
        sm = cnt['count__sum']
        return sm if sm is not None else 0

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.formatted_price)

class School(models.Model):
    # REVERSE: order_set

    name = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    product = models.ForeignKey(Product)
    max_people = models.IntegerField()


class Customer(models.Model):
    # REVERSE: order = OneToOne(Order)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=5)
    city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return u"%s %s" % (self.first_name, self.last_name)

    @property
    def sanitized_name(self):
        return u"".join(i for i in self.name if i.isalpha() or i in
            (u'ä', u'Ä', u'ö', u'Ö', u'å', u'Å', u'-', u"'", u" "))

    @property
    def name_and_email(self):
        return u"%s <%s>" % (self.sanitized_name, self.email)

class Order(models.Model):
    # REVERSE: order_product_set = ForeignKeyFrom(OrderProduct)

    customer = models.OneToOneField(Customer, null=True, blank=True)
    start_time = models.DateTimeField(auto_now=True)
    confirm_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=15, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    cancellation_time = models.DateTimeField(null=True, blank=True)
    batch = models.ForeignKey(Batch, null=True, blank=True)
    school = models.ForeignKey(School, null=True, blank=True)

    @property
    def is_active(self):
        return self.is_confirmed and not self.is_cancelled

    @property
    def is_outstanding(self):
        return self.is_confirmed and self.requires_shipping and not self.is_cancelled

    @property
    def is_confirmed(self):
        return self.confirm_time is not None

    @property
    def is_paid(self):
        return self.payment_date is not None

    @property
    def is_batched(self):
        return self.batch is not None

    @property
    def is_delivered(self):
        return self.is_batched and self.batch.is_delivered

    @property
    def is_overdue(self):
        return self.is_confirmed and not self.is_paid and self.due_date < datetime.now()

    @property
    def is_cancelled(self):
        return self.cancellation_time is not None

    @property
    def price_cents(self):
        # TODO Port to Django DB reduction functions if possible
        return sum(op.price_cents for op in self.order_product_set.all()) + self.shipping_and_handling_cents

    @property
    def shipping_and_handling_cents(self):
        return SHIPPING_AND_HANDLING_CENTS if self.requires_shipping else 0

    @property
    def formatted_shipping_and_handling(self):
        return format_price(self.shipping_and_handling_cents)

    @property
    def requires_shipping(self):
        # TODO do this in the database, too
        return any(op.product.requires_shipping for op in self.order_product_set.filter(count__gt=0))
    
    @property
    def formatted_price(self):
        return format_price(self.price_cents)

    @property
    def readable_state(self):
        if self.is_batched:
            return "Allocated into batch %d (%s)" % (self.batch.id, self.batch.readable_state)
        elif self.is_paid:
            return "Paid; awaiting allocation into batch"
        elif self.is_confirmed:
            if self.is_overdue:
                return "Confirmed; payment overdue since %s" % self.formatted_due_date
            else:
                return "Confirmed; payment due %s" % self.formatted_due_date
        else:
            return "Unconfirmed"

    @property
    def reference_number_base(self):
        return "5%04d" % self.pk

    @property
    def reference_number(self):
        s = self.reference_number_base
        return s + str(-sum(int(x)*[7,3,1][i%3] for i, x in enumerate(s[::-1])) % 10)

    @property
    def formatted_reference_number(self):
        return "".join((i if (n+1) % 5 else i+" ") for (n, i) in enumerate(self.reference_number[::-1]))[::-1]

    def confirm_order(self):
        assert self.customer is not None
        assert not self.is_confirmed

        self.order_product_set.filter(count__lte=0).delete()

        self.confirm_time = datetime.now()

        self.save()
        self.send_confirmation_message("tilausvahvistus")

    def confirm_payment(self, payment_date=None):
        assert self.is_confirmed
        
        if payment_date is None:
            payment_date = date.today()

        self.payment_date = payment_date

        self.save()        
        self.send_confirmation_message("maksuvahvistus")

    def cancel(self):
        assert self.is_confirmed

        self.cancellation_time = datetime.now()
        self.save()
        self.send_cancellation_notice_message()

    @property
    def deduplicated_product_messages(self):
        seen = set()
        result = list()

        for op in self.order_product_set.all():
            md = op.product.mail_description
    
            if md is not None:
                if md not in seen:
                    seen.add(md)
                    result.append(md)

        return result

    @property
    def email_vars(self):
        return dict(
            order=self,
            products=self.order_product_set.all(),
            messages=self.deduplicated_product_messages
        )

    @property
    def order_confirmation_message(self):
        return render_to_string("email/confirm_order.eml", self.email_vars)

    @property
    def payment_confirmation_message(self):
        return render_to_string("email/confirm_payment.eml", self.email_vars)

    @property
    def delivery_confirmation_message(self):
        return render_to_string("email/confirm_delivery.eml", self.email_vars)

    @property
    def payment_reminder_message(self):
        return render_to_string("email/payment_reminder.eml", self.email_vars)

    @property
    def cancellation_notice_message(self):
        return render_to_string("email/cancellation_notice.eml", self.email_vars)

    @property
    def due_date(self):
        if not self.confirm_time:
            return None

        else:
            return datetime.combine((self.confirm_time + timedelta(days=DUE_DAYS)).date(), dtime(23, 59, 59))

    @property
    def formatted_due_date(self):
        return format_date(self.due_date)

    def send_confirmation_message(self, msgtype):
        # don't fail silently, warn admins instead
        for op in self.order_product_set.filter(count__gt=0):
            if op.product.ilmoitus_mail:
                msgbcc = (settings.TICKET_SPAM_EMAIL, op.product.ilmoitus_mail)
            else:
                msgbcc = (settings.TICKET_SPAM_EMAIL,)
        
        if msgtype == "tilausvahvistus":
            msgsubject = "Tracon VI: Tilausvahvistus (#%04d)" % self.pk
            msgbody = self.order_confirmation_message
        elif msgtype == "maksuvahvistus":
            msgsubject = "Tracon VI: Maksuvahvistus (#%04d)" % self.pk
            msgbody = self.payment_confirmation_message
        elif msgtype == "toimitusvahvistus":
            msgsubject = "Tracon VI: Toimitusvahvistus (#%04d)" % self.pk
            msgbody = self.delivery_confirmation_message
        else:
            raise NotImplementedError(msgtype)
        
        EmailMessage(
            subject=msgsubject,
            body=msgbody,
            to=(self.customer.name_and_email,),
            bcc=msgbcc
        ).send(fail_silently=True)

    def send_payment_reminder_message(self):
        # TODO see above
        EmailMessage(
            subject="Tracon VI: Maksumuistutus (#%04d)" % self.pk,
            body=self.payment_reminder_message,
            to=(self.customer.name_and_email,),
            bcc=(settings.TICKET_SPAM_EMAIL,)
        ).send(fail_silently=True)

    def send_cancellation_notice_message(self):
        EmailMessage(
            subject="Tracon VI: Tilaus peruuntunut (#%04d)" % self.pk,
            body=self.cancellation_notice_message,
            to=(self.customer.name_and_email,),
            bcc=(settings.TICKET_SPAM_EMAIL,)
        ).send(fail_silently=True)

    def render(self, c):
        render_receipt(self, c)

    def __unicode__(self):
        return u"#%s %s (%s)" % (
            self.pk,
            self.formatted_price,
            self.readable_state
        )

    class Meta:
        permissions = (("can_manage_payments", "Can manage payments"),)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name="order_product_set")
    product = models.ForeignKey(Product, related_name="order_product_set")
    count = models.IntegerField(default=0)

    @property
    def target(self):
        return self.product

    @property
    def price_cents(self):
        return self.count * self.product.price_cents

    @property
    def formatted_price(self):
        return format_price(self.price_cents)

    def __unicode__(self):
        return u"%dx %s" % (
            self.count,
            self.product.name if self.product is not None else None
        )
