#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from collections import defaultdict

def main():
    confirmed_orders = Order.objects.filter(confirm_time__isnull=False)
    tickets_by_date = defaultdict(int)

    for order in confirmed_orders:
        date = order.confirm_time.date().isoformat()
        tickets_by_date[date] += order.tickets

    tickets_by_date = tickets_by_date.items()
    tickets_by_date.sort()

    for date, tickets in tickets_by_date:
        print "%s\t%s" % (date, tickets)

if __name__ == "__main__":
    main()
