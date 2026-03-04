from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

def notificar_tecnico_email(chamado):
    """
    Envia um email de notificação para o técnico responsável pelo chamado.
    Se o chamado não tiver um técnico atribuído, envia para todos os técnicos.
    """
    User = get_user_model()
    
    assunto = f"Novo chamado #{chamado.id}"
    remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@seusistema.com')
    destinatarios = []
    
    # Se já existir um técnico atribuído, manda apenas para ele
    if chamado.attributed_to and hasattr(chamado.attributed_to, 'email') and chamado.attributed_to.email:
        tecnico = chamado.attributed_to
        nome_tecnico = tecnico.first_name if tecnico.first_name else tecnico.username
        
        corpo = (
            f"Olá {nome_tecnico},\n\n"
            f"Um novo chamado foi aberto e atribuído a você.\n\n"
            f"Número do chamado: {chamado.id}\n"
            f"Descrição: {chamado.description}\n"
            f"Prioridade: {chamado.get_priority_display()}\n\n"
            f"Acesse o sistema para mais detalhes.\n"
        )
        destinatarios.append(tecnico.email)
        
    # Se NÃO existir técnico atribuído, manda para TODOS os técnicos
    else:
        # Pega todos os usuários que são técnicos e possuem e-mail válido
        tecnicos = User.objects.filter(is_technician=True).exclude(email__isnull=True).exclude(email="")
        
        # Pega a lista de e-mails
        destinatarios = [t.email for t in tecnicos]
        
        corpo = (
            f"Olá,\n\n"
            f"Um novo chamado foi aberto e está aguardando atribuição de um técnico.\n\n"
            f"Número do chamado: {chamado.id}\n"
            f"Descrição: {chamado.description}\n"
            f"Prioridade: {chamado.get_priority_display()}\n\n"
            f"Acesse o sistema para assumir o chamado.\n"
        )
        
    # Somente envia se houver destinatários
    if destinatarios:
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=remetente,
            recipient_list=destinatarios,
            fail_silently=False,
        )
