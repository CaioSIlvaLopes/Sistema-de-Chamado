from django.db import models
from django.conf import settings

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.CharField(max_length=400, blank=True, null=True)
    
    def __str__(self):
        return self.name

class SLAPolicy(models.Model):
    # Mapping to Ticket priorities
    PRIORITY_CHOICES =[
        ('DEF','desconhecido'),
        ('BAX','Baixa'),
        ('MED','Média'),
        ('ALT','Alta'),
        ('URG','Urgente'),
    ]
    
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, unique=True, verbose_name="Prioridade do Ticket")
    response_time_hours = models.IntegerField(default=4, verbose_name="Tempo para 1ª Resposta (Horas)")
    resolution_time_hours = models.IntegerField(default=24, verbose_name="Tempo para Resolução (Horas)")
    
    def __str__(self):
        return f"SLA {self.get_priority_display()} (Resp: {self.response_time_hours}h, Res: {self.resolution_time_hours}h)"

class Tickets (models.Model):
    STATUS_CHOICES = [
        ('SEM', 'Sem atendimento'),
        ('ABE', 'Aberto'),
        ('FEC', 'Fechado'),
    ]
    
    PRIORITY_CHOICES =[
        ('DEF','desconhecido'),
        ('BAX','Baixa'),
        ('MED','Média'),
        ('ALT','Alta'),
        ('URG','Urgente'),
        ]
    
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='Categoria')
    opened_by=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name='tickets_opened')
    attributed_to=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name='tickets_assigned', blank=True, null=True)
    description = models.CharField(max_length=400, blank=False, null=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='SEM')
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='DEF')
    opening_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    closing_date = models.DateTimeField(null=True, blank=True)
    attachment = models.ImageField(upload_to='attachment/', null=True, blank=True)
    
    # SLA Fields
    sla_response_due_at = models.DateTimeField(null=True, blank=True, verbose_name="SLA response")
    sla_resolution_due_at = models.DateTimeField(null=True, blank=True, verbose_name="SLA resolution")

    def __str__(self):
        return str(self.id)

class ChatMessage(models.Model):
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    attachment = models.ImageField(upload_to='chat_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Msg {self.id} on Ticket {self.ticket.id}"

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Notification for {self.recipient}: {self.title}"
