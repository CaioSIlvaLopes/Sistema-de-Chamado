
from django.contrib import admin
from django.urls import path
from tickets.views import novo_ticket, sucess_menssage
from users.views import profile
from tickets.views import ticket_detail
from tickets.views import meus_chamados
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_client
from django.shortcuts import redirect
from users.views import register_client
from tickets.views import ticket_reports

def redirect_to_login(request):
    return redirect('login_client')

urlpatterns = [
    path('', redirect_to_login),
    path('admin/', admin.site.urls),
    path('relatorios/',ticket_reports, name='ticket_reports'),
    path('chamados/', novo_ticket, name='novo_ticket'),
    path('mensagem_sucesso/<int:ticket_id>/',sucess_menssage, name='mensagem_de_sucesso'),
    path('meus-chamados/', meus_chamados, name='meus_chamados'),
    path('chamados/<int:ticket_id>/', ticket_detail, name='detail_chamado'),
    path('perfil/',profile,name='perfil'),
    path('login/', login_client, name='login_client'),
    path("register/", register_client, name="register_client"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
