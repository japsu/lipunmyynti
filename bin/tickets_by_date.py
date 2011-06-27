#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from collections import defaultdict

import datetime

# XXX hardkood0r
TICKET_PRODUCT_IDS = (1,2,3)

def main():
    confirmed_orders = Order.objects.filter(confirm_time__isnull=False, cancellation_time__isnull=True, order_product_set__product__id__in=TICKET_PRODUCT_IDS)
    tickets_by_date = defaultdict(int)

    for order in confirmed_orders:
        date = order.confirm_time.date()
        for op in order.order_product_set.filter(product__id__in=TICKET_PRODUCT_IDS):
            tickets_by_date[date] += op.count

    min_date = min(tickets_by_date.keys())
    max_date = max(tickets_by_date.keys())

    cur_date = min_date

    while cur_date <= max_date:
        tickets = tickets_by_date[cur_date]
        print "%s\t%s" % (cur_date.isoformat(), tickets)

        cur_date += datetime.timedelta(1)

if __name__ == "__main__":
    main()
