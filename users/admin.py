from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Enterprise

# Registra a empresa de forma simples
admin.site.register(Enterprise)

# Configura o Account usando o UserAdmin padrão do Django como base
@admin.register(Account)
class AccountAdmin(UserAdmin):
    # Colunas que aparecem na lista de usuários (CORREÇÃO AQUI: removemos 'name')
    list_display = ('username', 'email', 'first_name', 'last_name', 'enterprise', 'is_technician', 'is_staff')
    
    # Filtros laterais
    list_filter = ('is_technician', 'enterprise', 'is_staff', 'is_superuser', 'groups')
    
    # Campos de busca
    search_fields = ('username', 'first_name', 'last_name', 'email', 'enterprise__name')

    # Configuração do formulário de EDIÇÃO de usuário (dentro do admin)
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('enterprise', 'is_technician')}),
    )

    # Configuração do formulário de CRIAÇÃO de usuário (dentro do admin)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('enterprise', 'is_technician')}),
    )