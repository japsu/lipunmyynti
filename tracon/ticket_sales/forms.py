# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.localflavor.fi.forms import FIZipCodeField

from tracon.ticket_sales.models import *

__all__ = [
    "NullForm",
    "WelcomeForm",
    "OrderProductFormset",
    "OrderProductInlineFormset",
    "CustomerForm",
]

class NullForm(forms.Form):
    pass

class WelcomeForm(forms.ModelForm):
    class Meta:
        fields = []
        model = Order

OrderProductInlineFormset = forms.models.inlineformset_factory(
    Order,
    OrderProduct,
    fields=("count",),
    extra=0,
    can_delete=False
)

OrderProductFormset = forms.models.modelformset_factory(
    OrderProduct,
    exclude=("order", "product"),
    extra=0
)

ShirtOrderFormset = forms.models.modelformset_factory(
    ShirtOrder,
    exclude=("order", "product"),
    extra=0
)

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
