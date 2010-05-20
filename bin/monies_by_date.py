#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from collections import defaultdict

def main():
    confirmed_orders = Order.objects.filter(confirm_time__isnull=False)
    monies_by_date = defaultdict(int)

    for order in confirmed_orders:
        date = order.confirm_time.date().isoformat()
        monies_by_date[date] += order.price_cents

    monies_by_date = monies_by_date.items()
    monies_by_date.sort()

    for date, cents in monies_by_date:
        print "%s\t%s" % (date, "%d,%02d" % divmod(cents, 100))

if __name__ == "__main__":
    main()
