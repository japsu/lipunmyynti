# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.localflavor.fi.forms import FIZipCodeField

from tracon.ticket_sales.models import *

__all__ = [
    "NullForm",
    "WelcomeForm",
    "OrderProductForm",
    "ShirtOrderForm",
    "CustomerForm",
]

class NullForm(forms.Form):
    pass

class WelcomeForm(forms.ModelForm):
    class Meta:
        fields = []
        model = Order

class OrderProductForm(forms.ModelForm):
    count = forms.IntegerField(min_value=0)

    class Meta:
        exclude = ("order", "product")
        model = OrderProduct
        
class ShirtOrderForm(forms.ModelForm):
    count = forms.IntegerField(min_value=0)

    class Meta:
        exclude = ("order", "size")
        model = ShirtOrder

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
