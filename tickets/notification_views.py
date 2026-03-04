from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_view(request):
    filter_status = request.GET.get('filter', 'all')
    
    notifications = Notification.objects.filter(recipient=request.user)
    
    if filter_status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_status == 'read':
        notifications = notifications.filter(is_read=True)
        
    notifications = notifications.order_by('is_read', '-created_at')
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'current_filter': filter_status
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.ticket:
        return redirect('detail_chamado', ticket_id=notification.ticket.id)
    return redirect('notifications_view')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')
