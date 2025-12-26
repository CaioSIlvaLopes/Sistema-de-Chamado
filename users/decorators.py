from django.shortcuts import redirect


def client_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'client_id' not in request.session:
            return redirect('login_client')
        return view_func(request, *args, **kwargs)
    return wrapper
