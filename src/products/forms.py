from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
                validators=[MinValueValidator(1), MaxValueValidator(99)],
                widget=forms.TextInput(
                    attrs={
                        'type':"number",
                        'value':"1",
                        'min':"1",
                        'max':"99",
                        'aria-label':"Search",
                        'class':"form-control",
                        'style':"width: 100px",
                    }
                )
            )