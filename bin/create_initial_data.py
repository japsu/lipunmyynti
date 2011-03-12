#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *

PRODUCTS = [
    # (name, price_cents, classname, requires_shipping, sell_limit, available)
    ("Koko viikonlopun lippu", 1500, "large", True, 5000, True),
    ("Lauantailippu", 1000, "medium", True, 5000, True),
    ("Sunnuntailippu", 1000, "medium", True, 5000, True),
    ("Lattiamajoitus perjantain ja lauantain väliseksi yöksi", 700, "small", False, 500, False),
    ("Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi", 700, "small", False, 500, True),
    ("Taidekujapöytä", 1500, "small", False, 50, True)
]

def create_products():
    for name, price_cents, classname, requires_shipping, sell_limit, available in PRODUCTS:
        obj = Product(
            name=name,
            price_cents=price_cents,
            classname=classname,
            requires_shipping=requires_shipping,
            sell_limit=sell_limit,
            available=available
        )
        obj.save()

if __name__ == "__main__":
    create_products()
