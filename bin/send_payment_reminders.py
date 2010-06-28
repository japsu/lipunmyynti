#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import Order

DRY_RUN = False

def get_overdue_orders():
    # XXX iterates over all orders, baaad
    for order in Order.objects.all():
        if order.is_confirmed and order.requires_shipping and order.is_overdue:
            yield order

def send_payment_reminders():
    for order in get_overdue_orders():
	print order
	if not DRY_RUN:
	    order.send_payment_reminder_message()

if __name__ == "__main__":
    send_payment_reminders()
