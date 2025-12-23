from django import forms
from tickets.models import Category, Tickets

class TicketFormm(forms.Form):
    
    name_user=forms.CharField(max_length=100)
    name_enterprise=forms.CharField(max_length=100)
    department=forms.CharField(max_length=100)
    code_department=forms.CharField(max_length=20)
    category = forms.ModelChoiceField(Category.objects.all())
    description = forms.CharField(max_length=400)
    attachment = forms.ImageField()
    comments = forms.CharField(max_length=300)
    
    def save(self):
        ticket=Tickets(
            category = self.cleaned_data['name'],
            description = self.cleaned_data['description'],
            attachment = self.cleaned_data['attachment'],
            comments = self.cleaned_data['comments'],   
        )
        ticket.save()
        return ticket

class ModelTicketForm(forms.ModelForm):
    
    class Meta:
        model=Tickets
        fields ='__all__'
        
        
from django import forms
from .models import Tickets

class TicketForm(forms.ModelForm):
    class Meta:
        model = Tickets
        # Definimos apenas os campos que o usuário preenche
        fields = ['category', 'priority', 'description', 'attachment', 'comments']
        
        # Labels personalizados (opcional, para ficar bonito no HTML)
        labels = {
            'category': 'Categoria',
            'priority': 'Prioridade',
            'description': 'Descrição Detalhada',
            'attachment': 'Anexo',
            'comments': 'Comentários Adicionais'
        }

        # Widgets para inserir IDs e Placeholders do seu HTML original
        widgets = {
            'category': forms.Select(attrs={
                'id': 'categoria',
                'class': 'form-control', # Se estiver usando classes CSS globais
                # O Django já renderiza o select, o CSS cuida do resto
            }),
            'priority': forms.RadioSelect(attrs={
                'class': 'radio-input'
            }),
            'description': forms.Textarea(attrs={
                'id': 'descricao',
                'rows': 5,
                'placeholder': 'Descreva o problema de forma clara e objetiva...'
            }),
            'attachment': forms.FileInput(attrs={
                'id': 'anexo'
            }),
            'comments': forms.Textarea(attrs={
                'id': 'comentario',
                'rows': 3,
                'placeholder': 'Qualquer informação extra relevante.'
            })
        }