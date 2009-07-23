#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import ShirtSize

BASE_SIZES = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

NORMAL_NOT_AVAILABLE = ["XS"]
LADYFIT_NOT_AVAILABLE = ["XXL", "XXXL"]

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

if __name__ == "__main__":
    create_shirt_sizes()
