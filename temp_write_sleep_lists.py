#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from datetime import  datetime, timedelta
from csv import writer

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from ticket_sales.models import *

DRY_RUN = False
MESSAGE_SUBJECT = u"Tracon 8: Lattiamajoituksen ohje ({day_name} #{id:04d})"

PELA = Product.objects.get(name__icontains='pe-la')
LASU = Product.objects.get(name__icontains='la-su')

TAMMERKOSKI = School.objects.get(name__icontains='tammerkosk')
AMURI = School.objects.get(name__icontains='amuri')

def utf8(*args):
    return [unicode(arg).encode('UTF-8') for arg in args]

for (product, school, school_shortname, dayname) in [
    (PELA, TAMMERKOSKI, u"tammerkoski", u"perjantai"),
    (LASU, TAMMERKOSKI, u"tammerkoski", u"lauantai"),
    (LASU, AMURI,       u"amuri",       u"lauantai")
]:
    with open("{school_shortname}-{dayname}.csv".format(**locals()), 'w') as output_file:
        w = writer(output_file)
        w.writerow(utf8(school.name, dayname))
        for op in product.order_product_set.filter(order__school=school):
            w.writerow(utf8(op.order.customer.name, op.order.customer.phone_number, op.count))