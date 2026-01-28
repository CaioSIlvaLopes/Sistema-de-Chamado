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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from .tokens import account_activation_token

def register(request):
    if request.method == 'POST':
        print("DEBUG: Register POST request received")
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid")
            user = form.save(commit=False)
            user.is_active = False # Deactivate user until email is confirmed
            user.email_confirmed = False
            user.save()
            print(f"DEBUG: User {user.username} created (inactive)")

            # Email Confirmation Logic
            current_site = get_current_site(request)
            mail_subject = 'Ative sua conta - Sistema de Chamados'
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            print(f"DEBUG: Generated UID for link: {uid}")
            print(f"DEBUG: Generated Token for link: {token}")
            
            # Simple text message for now, or use a template
            activation_link = f"http://{current_site.domain}/users/activate/{uid}/{token}/"
            message = f"Olá {user.username},\n\nPor favor, clique no link abaixo para confirmar seu cadastro:\n\n{activation_link}\n\nObrigado!"
            
            print(f"\nDEBUG: --- CLICK THIS LINK TO ACTIVATE ---")
            print(f"{activation_link}")
            print(f"DEBUG: -----------------------------------\n")

            to_email = form.cleaned_data.get('email')
            print(f"DEBUG: Preparing to send email to {to_email}")
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            try:
                email.send()
                print("DEBUG: Email sent successfully via ConsoleBackend")
            except Exception as e:
                print(f"DEBUG: Error sending email: {e}")

            messages.success(request, 'Conta criada! Verifique seu email para confirmar o cadastro.')
            return redirect('registration_pending')
        else:
            print("DEBUG: Form is INVALID")
            print(form.errors)
    else:
        form = AccountRegisterForm()

    return render(request, 'register_client.html', {'form': form})

def registration_pending(request):
    return render(request, 'registration_pending.html')

def activate(request, uidb64, token):
    print(f"DEBUG: Activate view called with uidb64={uidb64}, token={token}")
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(f"DEBUG: Decoded UID: {uid}")
        user = User.objects.get(pk=uid)
        print(f"DEBUG: User found: {user.username} (ID: {user.pk})")
        print(f"DEBUG: Activate STATE - PK: {user.pk}, Password: {user.password}, LastLogin: {user.last_login}, Active: {user.is_active}, Joined: {user.date_joined}")
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(f"DEBUG: Error finding user: {e}")
        user = None

    if user is not None:
        token_valid = account_activation_token.check_token(user, token)
        print(f"DEBUG: Token valid? {token_valid}")
        
        if token_valid:
            user.is_active = True
            user.email_confirmed = True
            user.save()
            print("DEBUG: User activated successfully")
            messages.success(request, 'Email confirmado com sucesso! Agora você pode fazer login.')
            return redirect('login_client')
    
    print("DEBUG: Activation FAILED")
    messages.error(request, 'Link de ativação inválido ou expirado!')
    return redirect('login_client')

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
