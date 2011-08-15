#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
import sys

FORMAT=u"* ({order_id:04d}) {ordinal}. {name} - {phone} - {email} - {count} kpl - {payment_status}\n"
FWUP_FORMAT=u"* ({order_id:04d}) {ordinal}. {name}\n"
PRODUCT = Product.objects.get(name__icontains="Taidekuja")

def main(out=sys.stdout):
    orders = Order.objects.filter(
        order_product_set__product=PRODUCT,
        confirm_time__isnull=False,
        cancellation_time__isnull=True
    ).order_by("id")

    ordinal = 3

    for order in orders:
        count=order.order_product_set.get(product=PRODUCT).count
        payment_status="maksettu" if order.payment_date is not None else "MAKSAMATTA"

        args = dict(
            order_id=order.id,
            ordinal=ordinal,
            name=order.customer.name,
            phone=order.customer.phone_number,
            email=order.customer.email,
            count=count,
            payment_status=payment_status
        )
        out.write(FORMAT.format(**args).encode("UTF-8"))

        ordinal += 1

        if count > 1:
            args["ordinal"] = ordinal
            ordinal += 1

            out.write(FWUP_FORMAT.format(**args).encode("UTF-8"))
            
if __name__ == "__main__":
    main()
