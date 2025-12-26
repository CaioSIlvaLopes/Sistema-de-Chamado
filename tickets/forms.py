from django import forms
from tickets.models import Category, Tickets

from django import forms
from .models import Tickets


class TicketForm(forms.ModelForm):
    class Meta:
        model = Tickets
        fields = ['category', 'priority', 'description', 'attachment']
