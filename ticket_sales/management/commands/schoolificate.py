#!/usr/bin/env python
# encoding: utf-8
# vim: sw=4 et
import csv
import sys

from django.core.management.base import BaseCommand
from ticket_sales.models import *

def get_sleepy_order_set():
    return Order.objects.filter(
        # Is confirmed
        confirm_time__isnull=False,

        # Is paid
        payment_date__isnull=False,

        # Is not cancelled
        cancellation_time__isnull=True,

        # Contains lodging
        order_product_set__product__name__icontains=u'majoitus',

        # Has not been schoolificated yet
        school__isnull=True
    # First come, sleep closer
    ).order_by("confirm_time")

class Command(BaseCommand):
    args = '--really'
    help = 'Put sleeping people into schools'

    def handle(self, *args, **extra):
        dry_run = '--really' not in args

        possible_schools = list(School.objects.all().order_by("-priority"))

        for order in get_sleepy_order_set():
            sleepy_op = order.order_product_set.get(product__in=SLEEPY_PRODUCTS)

            for school in possible_schools:
                if sleepy_op.count < school.amount_available:
                    order.school = school
                    break

            if order.school:
                print order, sleepy_op.count, order.school
                if not dry_run:
                    order.save()
            else:
                print order, sleepy_op.count, "FAILED TO SCHOOLIFICATE"