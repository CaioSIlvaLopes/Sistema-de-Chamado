from django.db import models
from django.contrib.auth.models import AbstractUser

class Enterprise(models.Model):
    # O Django cria o ID automaticamente
    name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=14, unique=True) # unique garante que não duplique

    def __str__(self):
        return self.name

class Account(AbstractUser):
    # Removemos o campo 'password' (O AbstractUser já cuida disso com segurança)
    # Removemos o campo 'id' (O Django cria automaticamente)
    
    # Campo opcional (null=True, blank=True)
    # Isso permite que o Super Admin exista sem ter uma empresa vinculada
    enterprise = models.ForeignKey(
        Enterprise, 
        on_delete=models.PROTECT, 
        related_name='accounts', 
        verbose_name='Empresa',
        null=True,  
        blank=True
    )

    IS_TECH_CHOICES = (
        (False, 'Usuário'),
        (True, 'Técnico'),
    )
    is_technician = models.BooleanField(
        default=False, 
        verbose_name="É técnico?", 
        choices=IS_TECH_CHOICES
    )

    # O campo 'name' no seu código original é redundante, pois o AbstractUser
    # já tem 'first_name' e 'last_name'. Mas se quiser um nome de exibição único:
    display_name = models.CharField(max_length=200, verbose_name="Nome Completo", blank=True)
    
    email_confirmed = models.BooleanField(default=False, verbose_name="Email Confirmado")

    def __str__(self):
        return self.username