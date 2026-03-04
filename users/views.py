from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
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





from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
import random

def register(request):
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            # Generate 6 digit code
            codigo = str(random.randint(100000, 999999))
            
            # Save data and code into the session
            request.session['registration_data'] = request.POST.dict()
            request.session['verification_code'] = codigo

            # Email Confirmation Logic
            mail_subject = 'Código de Verificação - Sistema de Chamados'
            username_display = form.cleaned_data.get('username')
            message = f"Olá {username_display},\n\nSeu código de verificação é: {codigo}\n\nPor favor, insira este código no sistema para ativar sua conta.\n\nObrigado!"
            
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            try:
                email.send()
            except Exception as e:
                print(f"DEBUG: Error sending email: {e}")

            messages.success(request, 'Conta pré-aprovada! Verifique seu email para pegar o código de verificação e finalizar o cadastro.')
            return redirect('verify_email')
        else:
            print("DEBUG: Form is INVALID")
            print(form.errors)
    else:
        form = AccountRegisterForm()

    return render(request, 'register_client.html', {'form': form})

def verify_email(request):
    registration_data = request.session.get('registration_data')
    session_code = request.session.get('verification_code')
    
    if not registration_data or not session_code:
        messages.error(request, 'Sessão expirada ou não encontrada. Faça o cadastro novamente.')
        return redirect('register_client')

    if request.method == 'POST':
        codigo_digitado = request.POST.get('codigo')
        
        if codigo_digitado and codigo_digitado == session_code:
            from .forms import AccountRegisterForm
            
            form = AccountRegisterForm(registration_data)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True
                user.email_confirmed = True
                user.verification_code = None  # limpa o código após o uso
                user.save()
                
                # Setup session cleanup
                del request.session['registration_data']
                del request.session['verification_code']
                
                messages.success(request, 'Email confirmado com sucesso! Cadastro realizado. Agora você pode fazer login.')
                return redirect('login_client')
            else:
                messages.error(request, 'Houve um erro validando seus dados. Refaça o cadastro.')
                return redirect('register_client')
        else:
            messages.error(request, 'Código de verificação inválido!')
            
    email_display = registration_data.get('email', '')
    return render(request, 'registration_pending.html', {'email': email_display})

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
    tickets_resolved = Tickets.objects.filter(opened_by=client, status='FEC').count()
    tickets_active = chamados_abertos.count()
    
    context = {
        'client': client,
        'chamados_abertos': chamados_abertos,
        'tickets_resolved': tickets_resolved,
        'tickets_active': tickets_active,
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
    # Stats
    today = timezone.now().date()
    today_count = tickets.filter(opening_date__date=today).count()
    open_count = tickets.filter(status__in=['ABE', 'SEM']).count()
    urgent_count = tickets.filter(priority__in=['URG', 'ALT']).count()
    total_count = tickets.count()
    
    context = {
        'tech': tech, 
        'tickets': tickets,
        'today_count': today_count,
        'open_count': open_count,
        'urgent_count': urgent_count,
        'total_count': total_count,
    }
    
    return render(request, 'dashboard_technical.html', context)

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
