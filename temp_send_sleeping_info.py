#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import *
from datetime import  datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

DRY_RUN = False
MESSAGE_SUBJECT = u"Tracon 8: Lattiamajoituksen ohje ({day_name} #{id:04d})"

PELA = Product.objects.get(name__icontains='pe-la')
LASU = Product.objects.get(name__icontains='la-su')
TAMMERKOSKI = School.objects.get(name__icontains='tammerkosk')

def send_sleep_info(op):
    order = op.order

    vars = dict(
        id=order.id,
        name=order.customer.name,
        count=op.count,
        tammerkoski=(order.school == TAMMERKOSKI),
        perjantai=(op.product == PELA),
        day_name=("PERJANTAI" if op.product == PELA else "LAUANTAI")
    )

    body = render_to_string("email/sleep_info.eml", vars)
    subject = MESSAGE_SUBJECT.format(**vars)

    if not DRY_RUN:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=(order.customer.email,),
            bcc=[settings.TICKET_SPAM_EMAIL]
        ).send()

    print body

def send_all(product):
    for op in product.order_product_set.filter(order__school__isnull=False):
        send_sleep_info(op)

if __name__ == "__main__":
    send_all(PELA)
    send_all(LASU)
