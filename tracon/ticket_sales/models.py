# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from datetime import datetime

class DiscountCode(models.Model):
    code = models.CharField(max_length=16)
    discount = models.IntegerField()

class ProductInfo(models.Model):
    # REVERSE: order = OneToOne(Order)

    tickets = models.IntegerField(default=0)
    tickets_tshirts = models.IntegerField(default=0)
    tickets_accommodation = models.IntegerField(default=0)
    tickets_tshirts_accommodation = models.IntegerField(default=0)

    discount_code = models.OneToOneField(DiscountCode, null=True, blank=True)

    @property
    def tshirts(self):
        return self.tickets_tshirts + \
            self.tickets_tshirts_accommodation

    def __unicode__(self):
        return u"%dxL, %dxLP, %dxLM, %dxLPM" % (
            self.tickets,
            self.tickets_tshirts,
            self.tickets_accommodation,
            self.tickets_tshirts_accommodation
        )

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
    product_info = models.OneToOneField(ProductInfo, null=True, blank=True)
    customer = models.OneToOneField(Customer, null=True, blank=True)
    start_time = models.DateTimeField(auto_now=True)
    confirm_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=15, null=True, blank=True)
    payment_time = models.DateTimeField(null=True, blank=True)

    @property
    def is_confirmed(self):
        return self.confirm_time is not None

    @property
    def is_paid(self):
        return self.payment_time is not None

    def confirm(self):
        assert self.product_info is not None
        assert self.customer is not None

        self.confirm_time = datetime.now()

    def __unicode__(self):
        return u"#%s (%s %s)" % (
            self.pk,
            "Conf" if self.is_confirmed else "NotConf",
            "Paid" if self.is_paid else "NotPaid"
        )

class ShirtSize(models.Model):
    # REVERSE: shirt_set = ForeignKey(Shirt)

    name = models.CharField(max_length=5)
    ladyfit = models.BooleanField()
    available = models.BooleanField()

    def __unicode__(self):
        if self.ladyfit:
            return u"%s Ladyfit" % (self.name)
        else:
            return self.name

class ShirtOrder(models.Model):
    order = models.ForeignKey(Order)
    size = models.ForeignKey(ShirtSize)
    count = models.IntegerField()

    def __unicode__(self):
        return u"%dx%s" % (
            self.count,
            self.size
        )
