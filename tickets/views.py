from django.shortcuts import redirect, render
from tickets.forms import TicketForm

def tickets_view(request):
    if request.method =="POST":
        new_tickets_form = TicketForm(request.POST, request.FILES)
        if new_tickets_form.is_valid():
            new_tickets_form.save()
            return redirect('tickts_list')
    else:
        new_tickets_form=TicketForm()
    return render(request, 
                  'tickets.html',
                  {'new_ticket_form': new_tickets_form})