from tickets.models import Notification

def notification_counts(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {
            'unread_notifications_count': count,
            'has_unread_notifications': count > 0
        }
    return {}
