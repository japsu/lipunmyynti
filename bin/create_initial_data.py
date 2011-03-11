#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *

PRODUCTS = [
    ("Koko viikonlopun lippu", 1500, True),
    ("Lauantailippu", 1000, True),
    ("Sunnuntailippu", 1000, True),
    ("Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi", 700, False),
    ("Taidekujapöytä", 1500, False)
]

def create_products():
    for name, price_cents, requires_shipping in PRODUCTS:
        obj = Product(
            name=name,
            price_cents=price_cents,
            requires_shipping=requires_shipping
        )
        obj.save()

if __name__ == "__main__":
    create_products()
