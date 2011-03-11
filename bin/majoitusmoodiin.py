#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import Product

for p in Product.objects.all():
    p.available = False
    p.save()

# TODO minä olen poro, lailalalai, vanhentunut poro, lailalalai
Product(
    name="Majoituspaikka",
    price_cents=1000
).save()
