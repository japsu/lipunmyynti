# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.localflavor.fi.forms import FIZipCodeField

from tracon.ticket_sales.models import *

class NullForm(forms.Form):
    pass

class WelcomeForm(forms.ModelForm):
    class Meta:
        fields = []
        model = Order

class ProductInfoForm(forms.ModelForm):
    class Meta:
        model = ProductInfo

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
