from django.contrib import admin
from tickets.models import Tickets
from tickets.models import Category
from tickets.models import ChatMessage

class TicketsAdmin(admin.ModelAdmin):
    list_display=('id','category','status','priority','opened_by','attributed_to','description','opening_date','updated_date','closing_date','attachment','comments')
    search_fields=('id','opened_by','attributed_to','description','status','priority','opening_date','updated_date','closing_date',)
    list_filter = ('opened_by','attributed_to','status','opening_date','updated_date','closing_date',)

admin.site.register(Tickets, TicketsAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=('id','name','description')
    search_fields=('id','name')

admin.site.register(Category, CategoryAdmin)

class ChatMessageAdmin(admin.ModelAdmin):
    list_display=('id','ticket','sender','message','attachment','timestamp')
    search_fields=('id','ticket','sender','message','attachment','timestamp')
    list_filter = ('ticket','sender','message','attachment','timestamp',)

admin.site.register(ChatMessage, ChatMessageAdmin)