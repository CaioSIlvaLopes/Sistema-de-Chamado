# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account

class AccountRegisterForm(UserCreationForm):
    class Meta:
        model = Account
        # REMOVA 'name' desta lista.
        # ADICIONE 'first_name' e 'last_name' se quiser que o usuário digite o nome.
        fields = [
            'username', 
            'display_name', 
            'email', 
            'enterprise', 
            'is_technician'
        ]

    is_technician = forms.TypedChoiceField(
        choices=[(False, 'Usuário (Cliente)'), (True, 'Técnico de Suporte')],
        coerce=lambda x: x == 'True',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Conta'
    )