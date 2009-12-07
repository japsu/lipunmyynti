# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.localflavor.fi.forms import FIZipCodeField

from tracon.ticket_sales.models import *

__all__ = [
    "NullForm",
    "OrderProductForm",
    "ShirtOrderForm",
    "CustomerForm",
]

class HappyIntegerField(forms.IntegerField):
    def __init__(self, size=2):
        max_value = 10 ** size - 1

        super(HappyIntegerField, self).__init__(
            widget=forms.TextInput(attrs=dict(size=size, maxlength=size)),
            min_value=0,
            max_value=max_value
        )

    def clean(self, value):
        if not value:
            return 0

        else:
            return super(HappyIntegerField, self).clean(value)

class NullForm(forms.Form):
    pass

class OrderProductForm(forms.ModelForm):
    count = HappyIntegerField(2)

    class Meta:
        exclude = ("order", "product")
        model = OrderProduct
        
class ShirtOrderForm(forms.ModelForm):
    count = HappyIntegerField(3)

    class Meta:
        exclude = ("order", "size")
        model = ShirtOrder

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
