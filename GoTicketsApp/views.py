# Django imports
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.db.models import Model
from django.utils import timezone
from django.db.models.functions import Lower
from django.http import HttpRequest

# Forms and Models
from .forms import (
    CreateUserForm, EventForm, UpdateEventForm,
    PurchaseForm, SearchForm, UploadFileForm, CardForm
)
from .models import Event, User, Purchase, Card

# Other imports
from datetime import date
import json
import xml.etree.ElementTree as ET
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import reportlab
from PIL import Image
from io import BytesIO
from reportlab.lib.utils import ImageReader
import qrcode
from base64 import b64encode

# Custom Utilities
from .utils import generate_qr_code


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
            request.session['event_details'] = {
                'id': event.id,
                'title': event.title,
                'image_url': event.image.url if event.image else None,
                'description': event.description,
                'location': event.location,
                'start_date': str(event.start_date),
                'end_date': str(event.end_date),
                'price': str(event.price),
                'vip': purchase.vip,
                'quantity': purchase.quantity,

            }
            return redirect('checkout')
    else:
        form = PurchaseForm()

    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'GoTickets/events_by_id.html', context)



def checkout(request):
    event_details = request.session.get('event_details', {})

    if request.method == "POST":
        card = CardForm(request.POST)
        if card.is_valid():
            card.save()
            return redirect('order_confirmation')
    else:
        card = CardForm()

    context = {
        'card': card,
        'event': event_details,
    }

    return render(request, 'GoTickets/checkout.html', context)




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

def eventcreate(request: HttpRequest):
    upload_form = UploadFileForm()
    event_form = EventForm()

    if request.method == 'POST':
        if 'upload' in request.POST:
            upload_form = UploadFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                events = handle_uploaded_file(request.FILES['file'])
                # Store events in the session and add the logged-in user as the organizer
                for event in events:
                    event['organizer_id'] = request.user.id  # assuming organizer is a foreign key to User
                request.session['events'] = events
                return render(request, 'GoTickets/confirm_events.html', {'events': events})
        elif 'create' in request.POST:
            event_form = EventForm(request.POST, request.FILES)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                event.organizer = request.user  # set the organizer to the currently logged-in user
                event.save()
                return redirect('/events/')

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
            'title': child.findtext('title', default=''),  # Default to empty string if not found
            'description': child.findtext('description', default=''),
            'location': child.findtext('location', default=''),
            'start_date': child.findtext('start_date', default=''),
            'end_date': child.findtext('end_date', default=''),
            'price': child.findtext('price', default='0')  # Default price as '0' if not found
        }
        events.append(event)
    return events

def confirm_post(request: HttpRequest):
    events = request.session.get('events', [])
    if request.method == 'POST':
        if events and request.POST.get('confirm') == 'yes':
            for event in events:
                organizer_id = event.pop('organizer_id', None)  # Remove the organizer_id from the event dictionary
                if organizer_id:
                    Event.objects.create(**event, organizer_id=organizer_id)
            del request.session['events']
            return redirect('/events/')
        else:
            request.session.pop('events', None)
            return redirect('/upload/')

    return redirect('/upload/')

def ticket_confirmation(request, id):
    event = get_object_or_404(Event, pk=id)
    qr_img = generate_ticket_qr(id)  # Assuming generate_ticket_qr returns a PIL Image object

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_code_base64 = b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'GoTickets/ticket_confirmation.html', {
        'event': event,
        'qr_code_base64': qr_code_base64,
    })

def generate_ticket_qr(event_id):
    # Retrieve the event object or raise 404 if not found
    event = get_object_or_404(Event, pk=event_id)

    # Create ticket data dictionary
    ticket_data = {
        "title": event.title,
        "date": event.start_date.strftime('%Y-%m-%d'),
        "location": event.location,
    }

    # Convert ticket data to JSON and generate QR code
    qr = qrcode.QRCode(
        version=1,  # Adjust QR code version if necessary
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(ticket_data))
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill='black', back_color='white')

    # img is a PIL Image object and can be returned, saved, or manipulated further
    return img

def download_ticket_pdf(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    purchases = Purchase.objects.filter(event=event, user=request.user).order_by('-purchase_date')

    if not purchases.exists():
        return HttpResponse("No ticket purchases found.", status=404)

    qr_img = generate_ticket_qr(event_id)  # Get QR code as an image object
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = ImageReader(buffer)  # Convert the BytesIO stream to ImageReader

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{event.title}-ticket.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    for purchase in purchases:
        p.setFont("Helvetica-Bold", 14)
        p.drawString(72, height - 72, event.title)
        if event.image:
            p.drawImage(event.image.path, 72, height - 200, width=200, height=100)

        p.drawImage(qr_image, 280, height - 200, width=100, height=100)  # Use ImageReader object for QR code

        p.setFont("Helvetica", 12)
        p.drawString(72, height - 220, f"Organized by: {event.organizer.username if event.organizer else 'N/A'}")
        p.drawString(72, height - 240, "Location: " + event.location)
        p.drawString(72, height - 260, "Starts: " + event.start_date.strftime('%Y-%m-%d'))
        p.drawString(72, height - 280, "Ends: " + event.end_date.strftime('%Y-%m-%d'))
        p.drawString(72, height - 300, f"Price: ${event.price}")
        p.drawString(72, height - 320, f"VIP Access: {'Yes' if purchase.vip else 'No'}")
        p.drawString(72, height - 340, f"Quantity: {purchase.quantity}")
        p.drawString(72, height - 360, "Purchased on: " + purchase.purchase_date.strftime('%Y-%m-%d %H:%M'))

        p.showPage()

    p.save()
    return response
