from django.shortcuts import render, redirect
from users.models import Client
from users.decorators import client_login_required
from .forms import TicketForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Tickets


@client_login_required
def novo_ticket(request):

    current_client = Client.objects.get(
        id=request.session['client_id']
    )

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.opened_by = current_client
            ticket.save()
            return redirect('meus_chamados')
    else:
        form = TicketForm()

    return render(
        request,
        'new_ticket.html',
        {
            'form': form,
            'client': current_client
        }
    )
    
def meus_chamados(request):
    """
    Lista todos os chamados criados pelo usuário logado.
    """
    # Filtra os tickets pelo cliente que abriu
    chamados = Tickets.objects.filter(opened_by__login=request.user.username).order_by('-opening_date')

    context = {
        'chamados': chamados
    }

    return render(request, 'my_tickets.html', context)

@login_required
def ticket_detail(request, ticket_id):
    # pega o ticket
    ticket = get_object_or_404(Tickets, id=ticket_id)

    categoria=ticket.category
    # pega o cliente do ticket
    client = ticket.opened_by

    # pega o departamento do cliente
    departamento = client.department

    # se quiser, pode fazer permissão básica:
    # apenas o cliente ou técnico podem acessar
    # if not request.user.is_staff and request.user != client.user_field:
    #     return render(request, '403.html', status=403)

    context = {
        'ticket': ticket,
        'client': client,
        'departamento': departamento,
        'categoria' :categoria
    }

    return render(request, 'ticket_detail.html', context)

def ticket_reports(request):
    return render(request, 'tickets_reports.html')

@login_required
def profile(request):
    # Supondo que Client tenha um campo 'login' que é igual ao username do usuário
    client = get_object_or_404(Client, login=request.user.username)
    chamados_abertos = Tickets.objects.filter(opened_by=client, status__in=['SEM','ABE'])
    context = {
        'client': client, 
        'chamados_abertos': chamados_abertos,
    }
    return render(request, 'profile.html', context)
