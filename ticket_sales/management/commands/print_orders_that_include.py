#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

import csv
import sys

from django.core.management.base import BaseCommand
from ticket_sales.models import *

class Command(BaseCommand):
    args = '<id>'
    help = 'Print orders that include the given product'

    def handle(*args, **options):
      product_id = int(args.pop(0))
      assert len(args) == 0

      writer = csv.writer(sys.stdout)

      product = Product.objects.get(id=product_id)
      for op in product.order_product_set.filter(order__confirm_time__isnull=False, order__payment_date__isnull=False):
        order = op.order
        writer.write([op.order.customer.name, op.order.customer.email, op.count])