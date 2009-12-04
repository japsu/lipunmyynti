# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.localflavor.fi.forms import FIZipCodeField

from tracon.ticket_sales.models import *

__all__ = [
    "NullForm",
    "WelcomeForm",
    "OrderProductFormset",
    "ShirtOrderFormset",
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
        

OrderProductFormset = forms.models.modelformset_factory(
    OrderProduct,
    form=OrderProductForm,
    exclude=("order", "product"),
    extra=0,
    can_order=False,
    can_delete=False
)

class ShirtOrderForm(forms.ModelForm):
    count = forms.IntegerField(min_value=0)

    class Meta:
        exclude = ("order", "size")
        model = ShirtOrder

ShirtOrderFormset = forms.models.modelformset_factory(
    ShirtOrder,
    form=ShirtOrderForm,
    exclude=("order", "size"),
    extra=0,
    can_order=False,
    can_delete=False
)

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
