#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

# XXX Vanha accom-protokolla

from ticket_sales.models import Order
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

DRY_RUN = False

def get_applicable_orders():
    return Order.objects.filter(
        # Confirmed
        confirm_time__isnull=False,

        # Paid
        payment_time__isnull=False,

        # Not cancelled
        cancellation_time__isnull=True,
    )

def send_accom_info_message(order):
    vars = dict(order=order)
    body = render_to_string("email/accom_info_noslip.txt")
    subject = "Tracon V: Tietoa lattiamajoituksesta (#%04d)" % order.pk

    print subject

    if DRY_RUN:
        return

    EmailMessage(
        subject=subject,
        body=body,
        from_email="Tracon V Majoitus <majoitus10@tracon.fi>",
        to=(order.customer.name_and_email,),
        bcc=(settings.TICKET_SPAM_EMAIL,)
    ).send(fail_silently=True)
        
def main():
    orders = get_applicable_orders()

    for order in orders:
        if not order.requires_shipping and order.accommodation > 0:
            send_accom_info_message(order)

if __name__ == "__main__":
    main()
