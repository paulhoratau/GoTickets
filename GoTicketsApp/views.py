from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm, EventForm, UpdateEventForm, PurchaseForm
from .models import Event, User, Purchase





# Create your views here.
def index(request):
    return render(request, 'GoTickets/index.html')

def eventcreate(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('events')
    else:
        form = EventForm()
    return render(request, 'GoTickets/eventcreate.html', {'form': form})

def event_manage(request, id):  # Added 'id' as a parameter
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        form = UpdateEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('events')
        else:
            print(form.errors)  # Log or print form errors to debug
    else:
        form = UpdateEventForm(instance=event)
    return render(request, 'GoTickets/event_manage.html', {'form': form})

def events(request):
    events = Event.objects.all()
    context = {
        'events': events
    }
    return render(request, 'GoTickets/events.html', context)


def events_by_id(request, id):
    event = get_object_or_404(Event, pk=id)
    if request.method == "POST":
        form = PurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.event = event
            purchase.save()
            return redirect('order_confirmation')
    else:
        form = PurchaseForm()

    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'GoTickets/events_by_id.html', context)


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect ('login')
    context = {'form': form}
    return render(request, 'GoTickets/register.html', context)

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'GoTickets/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

def order_confirmation(request):
    return render(request, 'GoTickets/order_confirmation.html')

def checkout(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('order_confirmation')
    else:
        form = PurchaseForm()
    return render(request, 'GoTickets/checkout.html', {'form': form})
