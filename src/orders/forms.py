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
    use_default_ship    = forms.BooleanField(required=False)
    save_ship           = forms.BooleanField(required=False)
    country             = CountryField(blank_label='(select country)').formfield(
                                                                    required=False,
                                                                    widget=CountrySelectWidget(attrs={
                                                                        'class': 'custom-select d-block w-100',
                        }))
    payment_option      = forms.ChoiceField(
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
            ]
            
class PaymentForm(forms.ModelForm):
    use_default_bill    = forms.BooleanField(required=False)
    save_bill           = forms.BooleanField(required=False)
    country             = CountryField(blank_label='(select country)').formfield(
                                                                    required=False,
                                                                    widget=CountrySelectWidget(attrs={
                                                                        'class': 'custom-select d-block w-100',
                        }))
    
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
            ]
            
class CouponForm(forms.Form):
    code = forms.CharField(
            max_length=15,
            widget=forms.TextInput(
                attrs={
                    'class': "form-control",
                    'placeholder': "Promo code",
                    'aria-label': "Recipient's username",
                    'aria-describedby': "basic-addon2",
                }    
            )
        )