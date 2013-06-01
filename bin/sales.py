#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import *
from django.db.models import Q
from csv import writer
import sys

def main(stream=sys.stdout):
    w = writer(stream)

    for product in Product.objects.all():
        orps = product.order_product_set.filter(
            order__payment_time__isnull=False,
            order__confirm_time__isnull=False
        )

        total = sum(orp.count for orp in orps)

        w.writerow([product.name.encode("UTF-8"), total])
        

if __name__ == "__main__":
    main()
