#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import *
from collections import defaultdict

import datetime

def main():
    confirmed_orders = Order.objects.filter(confirm_time__isnull=False, cancellation_time__isnull=True)
    monies_by_date = defaultdict(int)

    for order in confirmed_orders:
        date = order.confirm_time.date()
        monies_by_date[date] += order.price_cents

    min_date = min(monies_by_date.keys())
    max_date = max(monies_by_date.keys())

    cur_date = min_date

    while cur_date <= max_date:
        cents = monies_by_date[cur_date]
        print "%s\t%s" % (cur_date.isoformat(), "%d,%02d" % divmod(cents, 100))

        cur_date += datetime.timedelta(1)

if __name__ == "__main__":
    main()
