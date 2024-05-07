from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm, EventForm, UpdateEventForm, PurchaseForm, SearchForm, UploadFileForm
from .models import Event, User, Purchase
from datetime import date
from django.db.models.functions import Lower
from django.utils import timezone
import xml.etree.ElementTree as ET
from decimal import Decimal
from django.db.models import Model
from .utils import generate_qr_code
import json
from django.urls import reverse




# Create your views here.
def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Event.objects.filter(title=query)
            return render(request, 'GoTickets/results.html', {'form': form, 'results': results})
    else:
        form = SearchForm()
    return render(request, 'GoTickets/index.html', {'form': form})



def event_manage(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        form = UpdateEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('events')
        else:
            print(form.errors)
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

def account(request):
    user = request.user

    context = {
        'user': user
    }
    return render(request, 'GoTickets/account.html', context)

def user_tickets(request):
    today = timezone.now().date()
    user_purchased_events_ids = Purchase.objects.filter(user=request.user).values_list('event', flat=True)

    expired_events = Event.objects.filter(id__in=user_purchased_events_ids, end_date__lt=today)
    valid_events = Event.objects.filter(id__in=user_purchased_events_ids, start_date__gt=today)

    return render(request, 'GoTickets/user_tickets.html', {
        'expired_events': expired_events,
        'valid_events': valid_events,
    })

def eventcreate(request):
    upload_form = UploadFileForm()
    event_form = EventForm()

    if request.method == 'POST':
        if 'upload' in request.POST:
            upload_form = UploadFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                events = handle_uploaded_file(request.FILES['file'])
                request.session['events'] = [event for event in events]  # Ensure all events are serializable
                return render(request, 'GoTickets/confirm_events.html', {'events': events})
        elif 'create' in request.POST:
            event_form = EventForm(request.POST, request.FILES)
            if event_form.is_valid():
                event = event_form.save(commit=False)  # Assumes EventForm is a ModelForm
                # Add any additional processing or field setting here
                event.save()  # Save the event to the database
                return redirect('/events/')  # Redirect to a confirmation page or similar

    return render(request, 'GoTickets/eventcreate.html', {
        'upload_form': upload_form,
        'event_form': event_form
    })


    return render(request, 'GoTickets/eventcreate.html', {
        'upload_form': upload_form,
        'event_form': event_form
    })


def handle_uploaded_file(f):
    tree = ET.parse(f)
    root = tree.getroot()
    events = []
    for child in root:
        event = {
            'title': child.find('title').text,
            'description': child.find('description').text,
            'location': child.find('location').text,
            'start_date': child.find('start_date').text,
            'end_date': child.find('end_date').text,
            'price': str(child.find('price').text)  # Ensure this is serializable
        }
        events.append(event)
    return events


def confirm_post(request):
    events = request.session.get('events', [])
    event_data = request.session.get('event_data', {})
    if request.method == 'POST':
        if events and request.POST.get('confirm') == 'yes':
            for event in events:
                Event.objects.create(**event)
            del request.session['events']
            return redirect('/events/')
        elif event_data and request.POST.get('confirm') == 'yes':
            Event.objects.create(**event_data)
            del request.session['event_data']
            return redirect('/events/')
        else:
            # Clear session for both events and event data on cancel
            request.session.pop('events', None)
            request.session.pop('event_data', None)
            return redirect('/upload/')

    return redirect('/upload/')  # Redirect if no POST data or no data in session

def ticket_confirmation(request, id):
    event = get_object_or_404(Event, pk=id)
    qr_url = reverse('event_qr', args=[event.id])
    context = {'event': event, 'qr_url': qr_url}
    return render(request, 'GoTickets/ticket_confirmation.html', context)

def generate_ticket_qr(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    ticket_data = {
        "title": event.title,
        "date": event.start_date.strftime('%Y-%m-%d'),
        "location": event.location,
    }
    img = generate_qr_code(json.dumps(ticket_data))
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response
