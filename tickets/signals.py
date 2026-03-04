from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tickets, SLAPolicy
from .utils import calculate_due_date
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Tickets)
def calculate_sla_dates(sender, instance, created, **kwargs):
    if created:
        try:
            # Find the policy for this ticket priority
            policy = SLAPolicy.objects.get(priority=instance.priority)
            
            # Use opening_date as start, assume it's set
            start_date = instance.opening_date
            
            # Calculate dates
            response_due = calculate_due_date(start_date, policy.response_time_hours)
            resolution_due = calculate_due_date(start_date, policy.resolution_time_hours)
            
            # Update fields directly to avoid infinite recursion if we called save() again
            # Although update() doesn't trigger signals, so it's safe. 
            # OR use logic like: check if fields are already set? But on create they aren't.
             
            Tickets.objects.filter(id=instance.id).update(
                sla_response_due_at=response_due,
                sla_resolution_due_at=resolution_due
            )
            
            logger.info(f"SLA calculated for Ticket {instance.id}: Resp {response_due}, Res {resolution_due}")
            
        except SLAPolicy.DoesNotExist:
            logger.warning(f"No SLA Policy found for priority {instance.priority}")
        except Exception as e:
            logger.error(f"Error calculating SLA for Ticket {instance.id}: {e}")

from .models import ChatMessage, Notification

@receiver(post_save, sender=ChatMessage)
def create_chat_notification(sender, instance, created, **kwargs):
    if created:
        ticket = instance.ticket
        msg_sender = instance.sender
        
        # Determine Recipient
        recipient = None
        
        # If sender is the ticket opener, notify the assigned tech (if any)
        if msg_sender == ticket.opened_by:
            if ticket.attributed_to:
                recipient = ticket.attributed_to
        
        # If sender is the assigned tech, notify the opener
        elif msg_sender == ticket.attributed_to:
            recipient = ticket.opened_by
            
        # Fallback/Edge case: If tech sends message but wasn't assigned (e.g. taking action), 
        # or if sender is neither (super admin?), logic can be expanded.
        # For now, simplistic dual comms:
        
        if not recipient:
            # Maybe the user sending is a tech but not THE assigned tech (yet), 
            # or maybe the user sending is the opener. 
            # Let's ensure strictness:
            if instance.sender.is_technician and ticket.opened_by != instance.sender:
                 recipient = ticket.opened_by
            elif not instance.sender.is_technician and ticket.attributed_to:
                 recipient = ticket.attributed_to
        
        if recipient and recipient != msg_sender:
            Notification.objects.create(
                recipient=recipient,
                ticket=ticket,
                title=f"Nova mensagem no chamado #{ticket.id}",
                message=f"{msg_sender.username}: {instance.message[:50]}..." if instance.message else "Nova imagem anexada."
            )
