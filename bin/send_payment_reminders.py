#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import Order
from datetime import  datetime, timedelta, date

DRY_RUN = False
#THRESHOLD = datetime.now() - timedelta(days=10)
THRESHOLD = datetime(2012, 8, 17)
DONT_SEND = []

def get_overdue_orders():
    # XXX iterates over all orders, baaad
    for order in Order.objects.all():
        if order.is_confirmed and not order.is_paid and not order.is_cancelled and order.id not in DONT_SEND and order.due_date < THRESHOLD:
            yield order

def send_payment_reminders():
    for order in get_overdue_orders():
	print order
	if not DRY_RUN:
	    order.send_payment_reminder_message()

if __name__ == "__main__":
    send_payment_reminders()
