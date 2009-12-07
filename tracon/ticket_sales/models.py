# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date, time
from django.core.mail import EmailMessage

__all__ = [
    "Batch",
    "Product",
    "Customer",
    "Order",
    "OrderProduct",
    "ShirtSize",
    "ShirtOrder"
]

TICKET_SPAM_ADDRESS = "Tracon V -lipputarkkailu <lipunmyyntispam10@tracon.fi>"
SHIPPING_AND_HANDLING_CENTS = 100

def format_price(cents):
    return u"%d,%02d €" % divmod(cents, 100)

def format_date(datetime):
    return datetime.strftime("%Y-%m-%d")

def format_datetime(datetime):
    return datetime.strftime("%Y-%m-%d %H:%M:%S")

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
    def readable_state(self):
        if self.is_delivered:
            return u"Delivered at %s" % format_date(self.delivery_time)
        elif self.is_prepared:
            return u"Prepared at %s; awaiting delivery" % format_date(self.prepare_time)
        elif self.is_printed:
            return u"Printed at %s; awaiting preparation" % format_date(self.print_time)
        else:
            return u"Awaiting print"

    def __unicode__(self):
        return u"#%d (%s)" % (
            self.pk,
            self.readable_state
        )

class Product(models.Model):
    name = models.CharField(max_length=100)
    price_cents = models.IntegerField()
    includes_tshirt = models.BooleanField(default=False)
    includes_accommodation = models.BooleanField(default=False)
    available = models.BooleanField(default=True)

    @property
    def formatted_price(self):
        return format_price(self.price_cents)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.formatted_price)

class Customer(models.Model):
    # REVERSE: order = OneToOne(Order)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=5)
    city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def sanitized_name(self):
        return u"".join(i for i in self.name if i.isalpha() or i in
            (u'ä', u'Ä', u'ö', u'Ö', u'å', u'Å', u'-', u"'", u" "))

    @property
    def name_and_email(self):
        return u"%s <%s>" % (self.sanitized_name, self.email)

class Order(models.Model):
    # REVERSE: order_product_set = ForeignKeyFrom(OrderProduct)
    # REVERSE: shirt_order_set = ForeignKeyFrom(ShirtOrder)

    customer = models.OneToOneField(Customer, null=True, blank=True)
    start_time = models.DateTimeField(auto_now=True)
    confirm_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=15, null=True, blank=True)
    payment_time = models.DateTimeField(null=True, blank=True)
    batch = models.ForeignKey(Batch, null=True, blank=True)

    @property
    def is_confirmed(self):
        return self.confirm_time is not None

    @property
    def is_paid(self):
        return self.payment_time is not None

    @property
    def is_batched(self):
        return self.batch is not None

    @property
    def price_cents(self):
        # TODO Port to Django DB reduction functions if possible
        return sum(op.price_cents for op in self.order_product_set.all()) + SHIPPING_AND_HANDLING_CENTS
    
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
            if datetime.now() < self.due_date:
                return "Confirmed; awaiting payment"
            else:
                return "Confirmed; payment overdue since %s" % self.formatted_due_date
        else:
            return "Unconfirmed"

    @property
    def tshirts(self):
        # TODO Port to Django DB reduction functions if possible
        return sum(op.count for op in
            self.order_product_set.filter(product__includes_tshirt=True))

    @property
    def accommodation(self):
        return sum(op.count for op in
            self.order_product_set.filter(product__includes_accommodation=True))

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

    def confirm(self):
        assert self.customer is not None
        assert self.confirm_time is None

        self.shirt_order_set.filter(count__lte=0).delete()
        self.order_product_set.filter(count__lte=0).delete()

        self.confirm_time = datetime.now()

        self.send_order_confirmation_message()

    @property
    def order_confirmation_message(self):
        vars = dict(
            order=self,
            products=self.order_product_set.all(),
            shirts=self.shirt_order_set.all()
        )

        return render_to_string("email/confirm_order.eml", vars)

    @property
    def due_date(self):
        if not self.confirm_time:
            return None

        return datetime.combine((self.confirm_time + timedelta(days=14)).date(), time(23, 59, 59))

    @property
    def formatted_due_date(self):
        return format_date(self.due_date)

    def send_order_confirmation_message(self):
        # TODO encap this, and don't fail silently, warn admins instead
        EmailMessage(
            subject="Tracon V: Tilausvahvistus (#%04d) KOEKÄYTÖSSÄ" % self.pk,
            body=self.order_confirmation_message,
            to=(self.customer.name_and_email,),
            bcc=(TICKET_SPAM_ADDRESS,)
        ).send(fail_silently=True)

    def __unicode__(self):
        return u"#%s %s (%s)" % (
            self.pk,
            self.formatted_price,
            self.readable_state
        )

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

class ShirtSize(models.Model):
    # REVERSE: shirt_order_set = ForeignKeyFrom(ShirtOrder)

    name = models.CharField(max_length=5)
    ladyfit = models.BooleanField()
    available = models.BooleanField()

    @property
    def readable_name(self):
        if self.ladyfit:
            return u"%s Ladyfit" % (self.name)
        else:
            return self.name

    def __unicode__(self):
        return self.readable_name

class ShirtOrder(models.Model):
    order = models.ForeignKey(Order, related_name="shirt_order_set")
    size = models.ForeignKey(ShirtSize, related_name="shirt_order_set")
    count = models.IntegerField(default=0)

    @property
    def target(self):
        return self.size

    def __unicode__(self):
        return u"%dx%s" % (
            self.count,
            self.size
        )
