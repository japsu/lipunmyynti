# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *
from django.contrib import admin

class CustomerInline(admin.StackedInline):
    model = Customer

class OrderProductInline(admin.TabularInline):
    model = OrderProduct

class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = [
        OrderProductInline,
#        CustomerInline
    ]

admin.site.register(Order, OrderAdmin)

for cls in (School, Batch, Product, Customer):
    admin.site.register(cls)
