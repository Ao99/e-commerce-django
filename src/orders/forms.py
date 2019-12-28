from django import forms
from django.db import models
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from accounts.models import Address

PAYMENT_CHOICES = (
    ('S', 'Credit/debit card via Stripe'),
    ('P', 'PayPal'),
)

class CheckoutForm(forms.ModelForm):
    country     = CountryField(blank_label='(select country)').formfield(
                                                                    widget=CountrySelectWidget(attrs={
                                                                        'class': 'custom-select d-block w-100',
                                                                    }))

    payment_option  = forms.ChoiceField(
                        choices = PAYMENT_CHOICES,
                        widget = forms.RadioSelect()
                    )
    
    class Meta:
        model = Address
        fields = [
                'first_name',
                'last_name',
                'email',
                'address',
                'address2',
                'city',
                'state',
                'country',
                'zip',
                'save_ship',
            ]