#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import Order
from datetime import  datetime, timedelta

DRY_RUN = False
THRESHOLD = datetime.now() - timedelta(days=2)

def get_cancellable_orders():
    # XXX iterates over all orders, baaad
    for order in Order.objects.all():
        if order.is_confirmed and order.requires_shipping and not order.is_paid and order.is_overdue and not order.is_batched:
            yield order

def send_payment_reminders():
    for order in get_cancellable_orders():
	print unicode(order).encode("UTF-8")
	if not DRY_RUN:
	    order.cancel()

if __name__ == "__main__":
    send_payment_reminders()
