from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from .models import Client, Enterprise


def login_client(request):
    error = None

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')

        try:
            client = Client.objects.get(login=login, password=password)
            request.session['client_id'] = client.id  
            return redirect('novo_ticket')
        except Client.DoesNotExist:
            error = 'Login ou senha inválidos'

    return render(request, 'login_client.html', {'error': error})



def register_client(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # ===== CRIAR USUÁRIO =====
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        # ===== CRIAR CLIENTE =====
        Client.objects.create(
            user=user,
        )

        messages.success(request, 'Cliente cadastrado com sucesso!')
        return redirect('login_client')

    return render(request, 'register_client.html', )

