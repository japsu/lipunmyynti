#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import *
from collections import defaultdict

import datetime

def main():
    confirmed_orders = Order.objects.filter(confirm_time__isnull=False, cancellation_time__isnull=True)
    orders_by_date = defaultdict(int)

    for order in confirmed_orders:
        date = order.confirm_time.date()
        orders_by_date[date] += 1

    min_date = min(orders_by_date.keys())
    max_date = max(orders_by_date.keys())

    cur_date = min_date

    while cur_date <= max_date:
        orders = orders_by_date[cur_date]
        print "%s\t%s" % (cur_date.isoformat(), orders)

        cur_date += datetime.timedelta(1)

if __name__ == "__main__":
    main()
