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

class DiscountCodeField(forms.Field):
    widget = forms.TextInput

    def clean(self, value):
        if not value:
            if self.required:
                raise forms.ValidationError([u"required"])
            else:
                return None

        try:
            discount_code = DiscountCode.objects.get(code=value)
        except DiscountCode.DoesNotExist:
            raise forms.ValidationError([u"invalid"])

        users = Order.objects.filter(
            product_info__discount_code__exact=discount_code,
            confirm_time__isnull=False
        )

        if users.exists():
            raise forms.ValidationError([u"used"])

        return discount_code

class ProductInfoForm(forms.ModelForm):
    discount_code = DiscountCodeField(required=False)

    class Meta:
        model = ProductInfo

class CustomerForm(forms.ModelForm):
    zip_code = FIZipCodeField()

    class Meta:
        model = Customer
