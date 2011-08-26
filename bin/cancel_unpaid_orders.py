#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import Order
from datetime import  datetime, timedelta

DRY_RUN = False
THRESHOLD = datetime.now() - timedelta(days=2)
DO_NOT_TOUCH = set((2,3,9,120,59,74,151,207,227,235,237,260,264,270,292,299,381))

def get_cancellable_orders():
    # XXX iterates over all orders, baaad
    for order in Order.objects.all():
        if order.is_confirmed and not order.is_paid and order.is_overdue and not order.is_batched and not order.is_cancelled and order.id not in DO_NOT_TOUCH:
            yield order

def send_payment_reminders():
    for order in get_cancellable_orders():
	print unicode(order).encode("UTF-8")
	if not DRY_RUN:
	    order.cancel()

if __name__ == "__main__":
    send_payment_reminders()
