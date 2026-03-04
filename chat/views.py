from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from tickets.models import Tickets, ChatMessage
import json

def chat_room(request, room_name='general'):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })

from django.urls import reverse

@login_required
def get_chat_messages(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    # Security check: user must be the opener or a technician
    if not request.user.is_technician and ticket.opened_by != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    messages = ChatMessage.objects.filter(ticket=ticket).order_by('timestamp')
    data = []
    for msg in messages:
        sender_name = msg.sender.username
        if hasattr(msg.sender, 'display_name') and msg.sender.display_name:
             sender_name = msg.sender.display_name
             
        # Add (Técnico) suffix if sender is tech
        if msg.sender.is_technician:
             sender_name += " (Técnico)"

        attachment_view_url = None
        if msg.attachment:
            attachment_view_url = reverse('view_chat_attachment', args=[msg.id])
             
        data.append({
            'sender': sender_name,
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%d/%m/%Y %H:%M'),
            'attachment_url': msg.attachment.url if msg.attachment else None,
            'attachment_view_url': attachment_view_url,
            'is_me': msg.sender == request.user
        })
        
    return JsonResponse({'messages': data})

@login_required
def view_chat_attachment(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)
    ticket = msg.ticket
    
    # Security check
    if not request.user.is_technician and ticket.opened_by != request.user:
        return redirect('meus_chamados')
        
    context = {
        'attachment_url': msg.attachment.url if msg.attachment else None,
        'back_url': reverse('detail_chamado', args=[ticket.id]),
        'filename': msg.attachment.name.split('/')[-1] if msg.attachment else 'Anexo'
    }
    return render(request, 'view_attachment.html', context)

@login_required
def send_chat_message(request, ticket_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Invalid method'})
        
    ticket = get_object_or_404(Tickets, id=ticket_id)
    if not request.user.is_technician and ticket.opened_by != request.user:
        return JsonResponse({'status': 'error', 'error': 'Unauthorized'}, status=403)
        
    message_text = request.POST.get('message', '')
    attachment = request.FILES.get('attachment')
    
    if not message_text and not attachment:
        return JsonResponse({'status': 'error', 'error': 'Empty message'})
        
    ChatMessage.objects.create(
        ticket=ticket,
        sender=request.user,
        message=message_text,
        attachment=attachment
    )
    
    return JsonResponse({'status': 'ok'})
