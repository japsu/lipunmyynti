#!/usr/bin/env python
# encoding: utf-8
# vim: sw=4 et

from ticket_sales.models import *
from create_schools import PERJANTAI

PE_PRODUCTS = Product.objects.filter(name__icontains="perjantain ja lauantain")

def get_pe_order_set():
    return Order.objects.filter(
        # Is confirmed
        confirm_time__isnull=False,

        # Is paid
        payment_date__isnull=False,

        # Is not cancelled
        cancellation_time__isnull=True,

        # Contains lodging
        order_product_set__product__in=PE_PRODUCTS,

    # First come, sleep closer
    ).order_by("confirm_time")

def schoolificate(orders):
    for order in orders:
        pe_op = order.order_product_set.get(product=PERJANTAI)

        if pe_op:
            print order, pe_op.count, order.school

if __name__ == "__main__":
    schoolificate(get_pe_order_set())
