#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *

PRODUCTS = [
    ("Koko viikonlopun lippu", 1500, True, True),
    ("Lauantailippu", 1000, True, True),
    ("Sunnuntailippu", 1000, True, True),
    ("Lattiamajoitus perjantain ja lauantain väliseksi yöksi", 700, False, False),
    ("Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi", 700, False, True),
    ("Taidekujapöytä", 1500, False, True)
]

def create_products():
    for name, price_cents, requires_shipping, available in PRODUCTS:
        obj = Product(
            name=name,
            price_cents=price_cents,
            requires_shipping=requires_shipping,
            available=available
        )
        obj.save()

if __name__ == "__main__":
    create_products()
