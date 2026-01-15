from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tickets
from .forms import TicketForm
from django.db.models import Count
from django.db.models.functions import ExtractMonth
import datetime

@login_required
def novo_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.opened_by = request.user
            ticket.save()
            return redirect('mensagem_de_sucesso', ticket_id=ticket.id)
    else:
        form = TicketForm()

    return render(
        request,
        'new_ticket.html',
        {
            'form': form,
            'client': request.user
        }
    )
    
@login_required
def meus_chamados(request):
    chamados = Tickets.objects.filter(opened_by=request.user).order_by('-opening_date')

    context = {
        'chamados': chamados,
        'client': request.user
    }

    return render(request, 'my_tickets.html', context)

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    opened_by = ticket.opened_by
    user = request.user
    
    is_tech = user.is_technician
    
    if is_tech:
        # Tech logic
        pass
    else:
        # Client logic: can only view own tickets
        if ticket.opened_by != user:
            return redirect('meus_chamados')
            
    # Calculate Business Seconds Left for SLA
    from django.utils import timezone
    from .utils import get_business_time_left
    
    # If ticket is closed, stop the timer at closing_date
    if ticket.status == 'FEC' and ticket.closing_date:
        reference_time = ticket.closing_date
    else:
        reference_time = timezone.now()
    
    sla_response_seconds = 0
    sla_resolution_seconds = 0
    
    if ticket.sla_response_due_at:
        sla_response_seconds = get_business_time_left(reference_time, ticket.sla_response_due_at)
        
    if ticket.sla_resolution_due_at:
        sla_resolution_seconds = get_business_time_left(reference_time, ticket.sla_resolution_due_at)

    context = {
        'ticket': ticket,
        'is_tech': is_tech,
        'tech': user if is_tech else None,
        'client': user if not is_tech else None,
        'opened_by': opened_by,
        # 'departamento': ... removed as Account does not have department
        'categoria': ticket.category,
        'sla_response_seconds': sla_response_seconds,
        'sla_resolution_seconds': sla_resolution_seconds,
    }
    return render(request, 'ticket_detail.html', context)
        

@login_required
def ticket_reports(request):
    client = request.user
    
    # Filter tickets by this client
    tickets = Tickets.objects.filter(opened_by=client)
    
    # Basic Stats
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status='ABE').count()
    closed_tickets = tickets.filter(status='FEC').count()
    pending_tickets = tickets.filter(status='SEM').count() # Sem atendimento
    
    # Monthly Stats for the Chart (Current Year)
    current_year = datetime.datetime.now().year
    
    monthly_data = tickets.filter(
        opening_date__year=current_year
    ).annotate(
        month=ExtractMonth('opening_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Initialize all months to 0
    stats_by_month = {m: 0 for m in range(1, 13)}
    for item in monthly_data:
        stats_by_month[item['month']] = item['count']
        
    # Normalize for chart height (percentage)
    max_count = max(stats_by_month.values()) if stats_by_month.values() else 1
    month_names = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
    
    chart_data = []
    for i in range(1, 13):
        count = stats_by_month[i]
        height = (count / max_count) * 100 if max_count > 0 else 0
        chart_data.append({
            'name': month_names[i-1],
            'count': count,
            'height': int(height)
        })

    # Donut Chart Percentages
    if total_tickets > 0:
        percent_open = (open_tickets / total_tickets) * 100
        percent_closed = (closed_tickets / total_tickets) * 100
    else:
        percent_open = 0
        percent_closed = 0
    
    end_open = percent_open
    end_closed = percent_open + percent_closed

    context={
        'client': client,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
        'pending_tickets': pending_tickets,
        'chart_data': chart_data,
        'end_open': end_open,
        'end_closed': end_closed,
    }
    return render(request, 'tickets_reports.html',context)

def sucess_menssage(request,ticket_id):
    ticket = get_object_or_404(Tickets, id=ticket_id)
    context = {
        'ticket': ticket,
    }
    return render(request,'sucess_message_ticket.html',context)


