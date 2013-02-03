#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import *
from csv import writer
import sys

def get_accom_orders():
    return Order.objects.filter(
        confirm_time__isnull=False,
        cancellation_time__isnull=True,
        school__isnull=False
    ).order_by("school__name","customer__last_name","customer__first_name")

def print_order_csv(orders, stream=sys.stdout):
    w = writer(stream)

    w.writerow(["Koulu", "Sukunimi", "Etunimi", u"Määrä".encode("ISO-8859-1"), "Kuitti"])

    for order in orders:
        firstname, lastname = order.customer.first_name, order.customer.last_name
        proof_required = "KUITTI!" if not order.is_paid else ""
        op = OrderProduct.objects.get(order=order, product=order.school.product)

        firstname = firstname.encode("ISO-8859-1")
        lastname = lastname.encode("ISO-8859-1")

        w.writerow([order.school.name.encode("ISO-8859-1"), lastname, firstname, op.count, proof_required])

def main():
    orders = get_accom_orders()
    print_order_csv(orders)

if __name__ == "__main__":
    main()
