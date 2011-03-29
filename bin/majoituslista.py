#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import Order
from csv import writer
import sys

DRY_RUN = False

def get_accom_orders():
    confirmed_orders = Order.objects.filter(
        confirm_time__isnull=False
    )

    for order in confirmed_orders:
        if not order.requires_shipping and order.accommodation > 0:
            yield order

def print_order_csv(orders, stream=sys.stdout):
    w = writer(stream)

    w.writerow(["Tnro", "Sukunimi", "Etunimi", u"Määrä".encode("ISO-8859-1"), "Kuitti"])

    for order in orders:
        firstname, lastname = order.customer.name.split(" ", 1)
        proof_required = "KUITTI!" if not order.is_paid else ""

        firstname = firstname.encode("ISO-8859-1")
        lastname = lastname.encode("ISO-8859-1")

        w.writerow([order.id, lastname, firstname, order.accommodation, proof_required])

def main():
    orders = get_accom_orders()
    print_order_csv(orders)

if __name__ == "__main__":
    main()
