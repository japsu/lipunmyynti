# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from datetime import datetime

__all__ = [
    "Batch",
    "Product",
    "Customer",
    "Order",
    "OrderProduct",
    "ShirtSize",
    "ShirtOrder"
]

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
    phone_number = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

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
        return sum(op.count * op.product.price_cents for op in
            self.order_product_set.all())
    
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
            return "Confirmed; awaiting payment"
        else:
            return "Unconfirmed"

    @property
    def tshirts(self):
        # TODO Port to Django DB reduction functions if possible
        return sum(op.count for op in
            self.order_product_set.filter(product__includes_tshirt = True))

    def confirm(self):
        assert self.customer is not None
        assert self.confirm_time is None

        self.confirm_time = datetime.now()

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

class ShirtSize(models.Model):
    # REVERSE: shirt_order_set = ForeignKeyFrom(ShirtOrder)

    name = models.CharField(max_length=5)
    ladyfit = models.BooleanField()
    available = models.BooleanField()

    def __unicode__(self):
        if self.ladyfit:
            return u"%s Ladyfit" % (self.name)
        else:
            return self.name

class ShirtOrder(models.Model):
    order = models.ForeignKey(Order, related_name="shirt_order_set")
    size = models.ForeignKey(ShirtSize, related_name="shirt_order_set")
    count = models.IntegerField()

    def __unicode__(self):
        return u"%dx%s" % (
            self.count,
            self.size
        )
