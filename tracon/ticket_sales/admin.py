# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from django.contrib import admin

for cls in (Batch, Product, Customer, Order, OrderProduct):
    admin.site.register(cls)
