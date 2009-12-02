# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.localflavor.fi.forms import FIZipCodeField

from tracon.ticket_sales.models import *

__all__ = [
    "NullForm",
    "WelcomeForm",
    "OrderProductFormset",
    "CustomerForm",
]

class NullForm(forms.Form):
    pass

class WelcomeForm(forms.ModelForm):
    class Meta:
        fields = []
        model = Order

OrderProductFormset = forms.models.modelformset_factory(
    OrderProduct,
    fields=("count")
)

ShirtOrderFormset = forms.models.modelformset_factory(
    ShirtOrder,
    fields=("count")
)

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
