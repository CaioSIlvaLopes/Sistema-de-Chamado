from django.contrib import admin
from users.models import Technical
from users.models import Client
from users.models import Enterprise

class TechnicalAdmin(admin.ModelAdmin):
    list_display=('id','name','number')
    search_fields=('id','name')

admin.site.register(Technical, TechnicalAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display=('id','name','department','enterprise')
    search_fields=('id','name','department')
    

admin.site.register(Client, ClientAdmin)



class EnterpriseAdmin(admin.ModelAdmin):
    list_display=('id','name','cnpj')
    search_fields=('id','name','cnpj')
    

admin.site.register(Enterprise, EnterpriseAdmin)