#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import Product

for p in Product.objects.all():
    p.available = False
    p.save()

Product(
    name="Majoituspaikka",
    includes_ticket=False,
    includes_tshirt=False,
    includes_accommodation=True,
    requires_shipping=False,
    price_cents=1000
).save()
