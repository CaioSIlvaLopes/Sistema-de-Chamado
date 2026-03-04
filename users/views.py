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

import random

def register(request):
    if request.method == 'POST':
        print("DEBUG: Register POST request received")
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid")
            # We don't save the user yet!
            # Instead, we store the cleaned data in the session
            registration_data = form.cleaned_data
            # Convert enterprise object to ID for session storage if it exists
            if registration_data.get('enterprise'):
                registration_data['enterprise_id'] = registration_data['enterprise'].id
                del registration_data['enterprise']
            
            # Generate 6-digit code
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Store data and code in session
            request.session['pending_registration'] = registration_data
            request.session['pending_verification_code'] = code
            request.session['verification_email'] = registration_data['email']
            
            print(f"DEBUG: Registration data stored in session. Verification code: {code}")

            # Email Confirmation Logic
            mail_subject = 'Ative sua conta - Sistema de Chamados'
            message = f"Olá {registration_data['username']},\n\nSeu código de verificação é: {code}\n\nPor favor, insira este código no site para ativar sua conta.\n\nObrigado!"
            
            to_email = registration_data['email']
            print(f"DEBUG: Preparing to send email to {to_email}")
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            try:
                email.send()
                print("DEBUG: Email sent successfully")
            except Exception as e:
                print(f"DEBUG: Error sending email: {e}")

            messages.success(request, 'Verifique seu email para obter o código de confirmação.')
            return redirect('registration_pending')
        else:
            print("DEBUG: Form is INVALID")
            print(form.errors)
    else:
        form = AccountRegisterForm()

    return render(request, 'register_client.html', {'form': form})

def registration_pending(request):
    email = request.session.get('verification_email', 'seu email')
    return render(request, 'registration_pending.html', {'email': email})

def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('codigo')
        registration_data = request.session.get('pending_registration')
        correct_code = request.session.get('pending_verification_code')
        
        if not registration_data or not correct_code:
            messages.error(request, 'Sessão expirada. Por favor, tente registrar novamente.')
            return redirect('register_client')
            
        if code == correct_code:
            # Code matches! Now we create the user
            password = registration_data.pop('password1') # AbstractUser doesn't have password1 field
            registration_data.pop('password2', None)
            
            # Handle enterprise_id
            enterprise_id = registration_data.pop('enterprise_id', None)
            
            user = Account(**registration_data)
            user.set_password(password)
            user.is_active = True
            user.email_confirmed = True
            
            if enterprise_id:
                from .models import Enterprise
                user.enterprise = Enterprise.objects.get(id=enterprise_id)
            
            user.save()
            print(f"DEBUG: User {user.username} successfully created and activated.")
            
            # Clear session
            del request.session['pending_registration']
            del request.session['pending_verification_code']
            
            login(request, user)
            messages.success(request, 'Email confirmado com sucesso! Bem-vindo.')
            if user.is_technician:
                return redirect('dashboard_technical')
            else:
                return redirect('novo_ticket')
        else:
            messages.error(request, 'Código inválido. Verifique seu email e tente novamente.')
            return render(request, 'registration_pending.html', {'email': registration_data['email']})
            
    return redirect('login_client')

def activate(request, uidb64, token):
    # Keep old activate view for compatibility if needed, but it's not being used anymore
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
