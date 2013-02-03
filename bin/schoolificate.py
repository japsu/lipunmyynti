#!/usr/bin/env python
# encoding: utf-8
# vim: sw=4 et

from tracon.ticket_sales.models import *
from send_sleeping_info import AMURI1K, AMURI2K, AMURI3K, PERJANTAIK, TAMMERKOSKIK, SLEEPY_PRODUCTS
from create_schools import PERJANTAI, TAMMERKOSKI1, AMURI1, AMURI2
DRY_RUN=False

def get_sleepy_order_set():
    return Order.objects.filter(
        # Is confirmed
        confirm_time__isnull=False,

        # Is paid
        payment_date__isnull=False,

        # Is not cancelled
        cancellation_time__isnull=True,

        # Contains lodging
        order_product_set__product__in=SLEEPY_PRODUCTS,

        # Has not been schoolificated yet
        school__isnull=True
    # First come, sleep closer
    ).order_by("confirm_time")

def schoolificate(orders):
    for order in orders:
        sleepy_op = order.order_product_set.get(product__in=SLEEPY_PRODUCTS)

        possible_schools = sleepy_op.product.school_set.all().order_by("-priority")

        for school in possible_schools:
            if sleepy_op.count < school.amount_available:
                order.school = school
                break

        if order.school:
            print order, sleepy_op.count, order.school
            if not DRY_RUN:
                order.save()
        else:
            print order, sleepy_op.count, "FAILED TO SCHOOLIFICATE"

if __name__ == "__main__":
    schoolificate(get_sleepy_order_set())
