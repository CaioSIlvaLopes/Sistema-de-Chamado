
from django.contrib import admin
from django.urls import path, include
from tickets.views import novo_ticket, sucess_menssage
from users.views import profile
from tickets.views import ticket_detail
from tickets.views import meus_chamados
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_view, logout_view
from django.shortcuts import redirect
from tickets.views import ticket_reports
from users.views import register, dashboard_technical, ticket_action, activate, registration_pending
from tickets.notification_views import notifications_view
from tickets.notification_views import mark_notification_read
from tickets.notification_views import mark_all_notifications_read

def redirect_to_login(request):
    return redirect('login_client')

urlpatterns = [
    path('', redirect_to_login),
    path('admin/', admin.site.urls),
    path('notificacoes/', notifications_view, name='notifications'),
    path('notificacoes/ler-todas/', mark_all_notifications_read, name='mark_all_read'),
    path('notificacoes/ler/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
    path('relatorios/',ticket_reports, name='ticket_reports'),
    path('chamados/', novo_ticket, name='novo_ticket'),
    path('mensagem_sucesso/<int:ticket_id>/',sucess_menssage, name='mensagem_de_sucesso'),
    path('meus-chamados/', meus_chamados, name='meus_chamados'),
    path('chamados/<int:ticket_id>/', ticket_detail, name='detail_chamado'),
    path('chat/', include('chat.urls')),

    
    path('perfil/',profile,name='perfil'),
    path('login/', login_view, name='login_client'),
    path('logout/', logout_view, name='logout_client'),
    path("Cadastro/", register, name="register_client"),
    path('users/pending/', registration_pending, name='registration_pending'),
    path('users/activate/<str:uidb64>/<str:token>/', activate, name='activate'),

    # Técnicos (Dashboard e Ações)
    path("tecnico/dashboard/", dashboard_technical, name="dashboard_technical"),
    path("tecnico/acao/<int:ticket_id>/<str:action>/", ticket_action, name="ticket_action"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
