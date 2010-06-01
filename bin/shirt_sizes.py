#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from csv import writer
from collections import defaultdict

import csv
import sys

def main():
    shirts_per_size = defaultdict(int)

    for shirt_order in ShirtOrder.objects.filter(
            order__isnull=False,
            order__confirm_time__isnull=False):
        shirts_per_size[shirt_order.size] += shirt_order.count

    shirts_per_size = shirts_per_size.items()
    shirts_per_size.sort(key=lambda x: x[0].id)

    writer = csv.writer(sys.stdout)
    writer.writerows(shirts_per_size)

if __name__ == "__main__":
    main()
