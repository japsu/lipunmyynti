#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *

BASE_SIZES = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"]

NORMAL_NOT_AVAILABLE = ["XS"]
LADYFIT_NOT_AVAILABLE = ["3XL", "4XL", "5XL"]

def create_shirt_sizes():
    # Create normal sizes
    for size in BASE_SIZES:
        available = size not in NORMAL_NOT_AVAILABLE
        obj = ShirtSize(name=size, ladyfit=False, available=available)
	obj.save()

    # Create ladyfit sizes
    for size in BASE_SIZES:
        available = size not in LADYFIT_NOT_AVAILABLE
        obj = ShirtSize(name=size, ladyfit=True, available=available)
	obj.save()

PRODUCTS = [
    ("Ennakkolippu ja T-paita", 2200, True, False),
    ("Ennakkolippu, T-paita ja lattiamajoitus", 3200, True, True),
    ("Ennakkolippu ja lattiamajoitus", 1900, False, True),
    ("Pelkkä ennakkolippu", 900, False, False),
]

def create_products():
    for name, price_cents, tshirt, accom in PRODUCTS:
        obj = Product(
            name=name,
            price_cents=price_cents,
            includes_tshirt=tshirt,
            includes_accommodation=accom
        )
        obj.save()

if __name__ == "__main__":
    create_shirt_sizes()
    create_products()
