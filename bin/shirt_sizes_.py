#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from csv import writer
from collections import defaultdict

import csv
import sys

def main():
    writer = csv.writer(sys.stdout)

    for shirt_size in ShirtSize.objects.all().order_by("id"):
        n = sum(i.count for i in shirt_size.shirt_order_set.filter(
            order__confirm_time__isnull=False,
            order__cancellation_time__isnull=True
        ))

        writer.writerow((shirt_size, n))

if __name__ == "__main__":
    main()
