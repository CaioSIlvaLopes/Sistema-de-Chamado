from django.contrib import admin
from users.models import Technical
from users.models import Client

class TechnicalAdmin(admin.ModelAdmin):
    list_display=('id','name','number')
    search_fields=('id','name')

admin.site.register(Technical, TechnicalAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display=('id','name','department')
    search_fields=('id','name','department')
    

admin.site.register(Client, ClientAdmin)