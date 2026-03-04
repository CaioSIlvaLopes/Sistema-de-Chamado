from django.utils import timezone
from celery import shared_task
from .models import Tickets, Notification
from .utils import get_business_time_left
import logging
import datetime

logger = logging.getLogger(__name__)

@shared_task
def check_sla_breaches():
    now = timezone.now()
    
    # 1. Check for BREACHES (Already overdue)
    breached_resolution = Tickets.objects.filter(
        status__in=['ABE', 'SEM'],
        sla_resolution_due_at__lt=now
    )
    
    for ticket in breached_resolution:
        # We should avoid spamming the database with notifications if one already exists for this specific breach?
        # A simple way for MVP is just logging, or checking if a "Breach" notification exists recently.
        # For this request, user asked for "Warning at 30 minutes", so let's focus on that below.
        pass

    # 2. Check for WARNINGS (Approaching deadline)
    # We want tickets where SLA is in future, but less than 30 minutes away (business time or real time?)
    # User said "Warning if SLA time is at 30 minutes".
    # Let's filter tickets that are NOT breached yet.
    
    open_tickets = Tickets.objects.filter(
        status__in=['ABE', 'SEM'],
        sla_resolution_due_at__gt=now
    )
    
    warning_threshold_seconds = 30 * 60 # 30 minutes
    
    for ticket in open_tickets:
        # Calculate business seconds left
        seconds_left = get_business_time_left(now, ticket.sla_resolution_due_at)
        
        # We want to catch them when they fall into the window [0, 30min]
        # BUT we must ensure we don't send duplicates every 5 mins.
        # We can check if a warning notification was already sent?
        # Or add a flag to the ticket. simpler: just check if we sent a notification with this title recently?
        
        if 0 < seconds_left <= warning_threshold_seconds:
             # Check for existing warning
             # This is a bit resource intensive loop, but fine for small scale. 
             # Ideally we'd have a 'sla_warning_sent' boolean on Ticket.
             
             # Let's assume we add a boolean to models, or we do a quick check on Notifications.
             already_notified = Notification.objects.filter(
                 ticket=ticket,
                 title__contains="Atenção: SLA Expirando"
             ).exists()
             
             if not already_notified:
                 # Who to notify? The assigned tech. If none, maybe the opener? or admins (not implemented).
                 # Priority: Attributed Tech > Opener (if they are observing? usually admins monitor sla)
                 # Let's notify the attributed tech.
                 
                 recipient = ticket.attributed_to
                 if recipient:
                     Notification.objects.create(
                        recipient=recipient,
                        ticket=ticket,
                        title=f"Atenção: SLA Expirando - Chamado #{ticket.id}",
                        message=f"O prazo de resolução vence em menos de 30 minutos!"
                     )
                     logger.info(f"SLA Warning sent for Ticket {ticket.id}")
    
    return "SLA Check Completed"
