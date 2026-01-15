from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from tickets.models import Tickets
from .forms import AccountRegisterForm
from .models import Account

def login_view(request):
    if request.method == 'POST':
        # Assuming the HTML input name is 'login' and mapped to username
        username = request.POST.get('login')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_technician:
                return redirect('dashboard_technical')
            else:
                return redirect('novo_ticket')
        else:
            messages.error(request, 'Login ou senha inválidos')

    return render(request, 'login_client.html')

def logout_view(request):
    logout(request)
    return redirect('login_client')





def register(request):
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login_client')
    else:
        form = AccountRegisterForm()

    return render(request, 'register_client.html', {'form': form})

@login_required
def profile(request):
    client = request.user
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        if name:
            client.display_name = name
        if email:
            client.email = email
            
        client.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')

    chamados_abertos = Tickets.objects.filter(opened_by=client, status__in=['SEM','ABE'])
    context = {
        'client': client,
        'chamados_abertos': chamados_abertos,
    }
    return render(request, 'profile.html', context)

# --- TÉCNICOS ---

@login_required
def dashboard_technical(request):
    if not request.user.is_technician:
        return redirect('novo_ticket')
    
    tech = request.user
    # Todos os chamados.
    tickets = Tickets.objects.all().order_by('-opening_date')
    
    return render(request, 'dashboard_technical.html', {'tech': tech, 'tickets': tickets})

@login_required
def ticket_action(request, ticket_id, action):
    if not request.user.is_technician:
        return redirect('novo_ticket')
        
    tech = request.user
    ticket = get_object_or_404(Tickets, id=ticket_id)
    
    if action == 'receive':
        ticket.attributed_to = tech
        ticket.status = 'ABE' # Aberto / Em atendimento
        ticket.save()
        messages.success(request, f'Chamado #{ticket.id} assumido com sucesso.', extra_tags='ticket_message')
        
    elif action == 'finalize':
        if ticket.attributed_to == tech:
            ticket.status = 'FEC'
            ticket.save()
            messages.success(request, f'Chamado #{ticket.id} finalizado.', extra_tags='ticket_message')
        else:
            messages.error(request, 'Você não pode finalizar um chamado que não assumiu.', extra_tags='ticket_message')

    return redirect('dashboard_technical')
