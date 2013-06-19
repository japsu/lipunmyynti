#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import *

DAYS = [
    (u'Koko viikonlopun lippu', u'koko tapahtuman ajan (la klo 10 - su klo 18)',    (1550, 1750)),
    (u'Lauantailippu',          u'lauantain ajan (la klo 10 - su klo 08',           (1050, 1250)),
    (u'Sunnuntailippu',         u'sunnuntain ajan (su klo 00 - su klo 18',          (1050, 1250)),
]

METHODS = [
    # short description, requires shipping, available at launch, long description
    (u'postitse',   True,   True,   u'postitse kotiisi'),
    (u'e-lippu',    False,  False,  u'sähköisesti ja vaihdat sen rannekkeeseen tapahtumapaikalla'),
]

NUM_STEPS = len(DAYS[0][3])

def create_tickets():
    ordering = 0
    for step_idx in xrange(NUM_STEPS):
        internal_description = u"{}. porras".format(step_idx + 1)
        step_available = step_idx == 0

        for name, validity, step_price_centsies in DAYS:
            for method_name, requires_shipping, method_available, method_description in METHODS:
                description = u"Lippu toimitetaan {method_description} ja se on voimassa {validity}.".format(**locals())
                ordering += 100

                Product.objects.create(
                    name=name,
                    internal_description=internal_description,
                    price_cents=price_cents,
                    description=description,
                    mail_description=mail_description,
                    requires_shipping=requires_shipping,
                    sell_limit=sell_limit,
                    available=step_available and method_available,
                    ordering=ordering
                )


if __name__ == "__main__":
    create_tickets()
