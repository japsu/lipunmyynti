#!/usr/bin/env python
# encoding: utf-8
# vim: sw=4 et

from tracon.ticket_sales.models import *
from send_sleeping_info import CLASU, TAMMERKOSKI, KAUKAJARVI, SLEEPY_PRODUCTS
from create_schools import KAUKKIS, PERUS

def schoolificate():
    orders = Order.objects.filter(
        # Is confirmed
        confirm_time__isnull=False,

        # Is paid
        payment_date__isnull=False,

        # Is not cancelled
        cancellation_time__isnull=True,

        # Contains lodging
        order_product_set__in=SLEEPY_PRODUCTS

    # First come, sleep closer
    ).order_by("confirm_time")

    print orders.count()

if __name__ == "__main__":
    schoolificate()
