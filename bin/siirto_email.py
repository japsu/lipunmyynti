#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from datetime import  datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

DRY_RUN = False
MESSAGE_SUBJECT = u"TÄRKEÄÄ: Tracon-majoituksesi joudutaan siirtämään Amurin koululle (#{id:04d})"

SLEEPY_PRODUCTS = Product.objects.filter(name__icontains="lauantain ja sunnuntain")

AMURI3K = School.objects.get(name__icontains="siirretyt")

def send_sleep_info(order):
    op = order.order_product_set.get(product__in=SLEEPY_PRODUCTS)

    vars = dict(
        id=order.id,
        nimi=order.customer.name,
        maara=op.count
    )

    body=render_to_string("email/siirto.eml", vars)
    subject=MESSAGE_SUBJECT.format(**vars)

    if not DRY_RUN:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=(order.customer.email,),
            bcc=["liput12@tracon.fi"]
        ).send()

    print order

def main():
    orders = Order.objects.filter(school=AMURI3K)
    for order in orders:
        send_sleep_info(order)

if __name__ == "__main__":
    main()
