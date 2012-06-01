#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from datetime import  datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

DRY_RUN = False
MESSAGE_SUBJECT = u"Tracon VI: Lattiamajoituksen ohje (#{id:04d})"

SLEEPY_PRODUCTS = Product.objects.filter(name__icontains="majoitus")

CLASU = School.objects.get(name="Klassillinen koulu")
TAMMERKOSKI = School.objects.get(name="Tammerkosken koulu")
KAUKAJARVI = School.objects.get(name__icontains="Kaukaj")

def send_sleep_info(order):
    op = order.order_product_set.get(product__in=SLEEPY_PRODUCTS)

    vars = dict(
        id=order.id,
        name=order.customer.name,
        count=op.count,
        school=order.school.name,
        address=order.school.address,
        clasu=(order.school == CLASU),
        tammerkoski=(order.school == TAMMERKOSKI),
        kaukajarvi=(order.school == KAUKAJARVI)
    )

    body=render_to_string("email/sleep_info.eml", vars)
    subject=MESSAGE_SUBJECT.format(**vars)

    if not DRY_RUN:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=(order.customer.email,),
            bcc=(settings.TICKET_SPAM_EMAIL,)
        ).send()

    print order

def main():
    # XXX PURKKA
    orders = Order.objects.filter(school=KAUKAJARVI)
    for order in orders:
        send_sleep_info(order)

if __name__ == "__main__":
    main()
