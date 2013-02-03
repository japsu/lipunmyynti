#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from datetime import  datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

DRY_RUN = False
MESSAGE_SUBJECT = u"Tracon 7: Lattiamajoituksen ohje (#{id:04d})"

SLEEPY_PRODUCTS = Product.objects.filter(name__icontains="lauantain ja sunnuntain")

PERJANTAIK = School.objects.get(name__icontains="pe-la")
TAMMERKOSKIK = School.objects.get(name__icontains="la-su")
AMURI1K = School.objects.get(name__icontains="virheelliset")
AMURI2K = School.objects.get(name__icontains="tavalliset")
AMURI3K = School.objects.get(name__icontains="siirretyt")

def send_sleep_info(order):
    op = order.order_product_set.get(product__in=SLEEPY_PRODUCTS)

    vars = dict(
        id=order.id,
        name=order.customer.name,
        count=op.count,
        tammerkoski=(order.school == TAMMERKOSKIK),
        perjantai=(order.school == PERJANTAIK)
    )

    body=render_to_string("email/sleep_info.eml", vars)
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
    orders = Order.objects.filter(school__isnull=False)
    for order in orders:
        send_sleep_info(order)

if __name__ == "__main__":
    main()
