# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from django.db.models import Model, Sum
from django.db.models.functions import Lower
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required



# Forms and Models
from .models import Event, User, Purchase, Card, Ticket
from .forms import (
    CreateUserForm, EventForm, UpdateEventForm,
    PurchaseForm, SearchForm, UploadFileForm, CardForm, CustomPasswordChangeForm, TicketForm, UpdateUserForm, UserProfileForm, SearchEventForm, FilterForm
)

# Third-party libraries
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
    if request.method == 'GET':
        form = SearchForm()
        return render(request, 'GoTickets/index.html', {'form': form})
    return render(request, 'GoTickets/index.html')


@login_required
def event_manage(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user != event.organizer:
        raise PermissionDenied("You are not allowed to edit this event.")
    if request.method == 'POST':
        form = UpdateEventForm(request.POST, instance=event)
        if form.is_valid():
            db_obj = form.save(commit = False)
            db_obj.organizer_id = request.user
            print(db_obj.__dict__)
            db_obj.save()
            messages.success(request, f'Your event has been modified!')
    else:
        form = UpdateEventForm(instance=event)
    return render(request, 'GoTickets/event_manage.html', {'form': form, 'event': event})

@login_required
def events(request):
    context = {}
    all_events = Event.objects.all()
    top_events = Event.objects.annotate(total_purchases=Sum('purchase__quantity')).order_by('-total_purchases')[:2]
    if request.method == 'GET':
        context = {
            'events': all_events,
            'top_events': top_events
        }
        return render(request, 'GoTickets/events.html', context)

    elif request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']

            if from_date and to_date:
                filtered_events = Event.objects.filter(
                title__icontains=query,
                start_date__gte=from_date,
                end_date__lte=to_date
                )
            else:
                filtered_events = Event.objects.filter(title__icontains=query)

            context = {
                'form': form,
                'events': filtered_events,
                'top_events': top_events
            }
        else:
            context = {
                'form': form,
                'events': all_events,
                'top_events': top_events
            }
        return render(request, 'GoTickets/events.html', context)





@login_required
def event_by_id(request, id):
    event = get_object_or_404(Event, pk=id)
    tickets = Ticket.objects.filter(event=event)

    total_purchased = event.purchase_set.aggregate(Sum('quantity'))['quantity__sum'] or 0
    remaining_seats = event.seats - total_purchased

    if request.method == "POST":
        form = PurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            quantity_requested = form.cleaned_data['quantity']
            if quantity_requested > remaining_seats:
                messages.error(request, "Only {remaining_seats} tickets are available.")
            else:
                purchase_details = {
                    'user_id': request.user.id,
                    'event_id': event.id,
                    'quantity': quantity_requested,
                }
                request.session['purchase_details'] = purchase_details
                request.session['event_details'] = {
                    'id': event.id,
                    'title': event.title,
                    'image_url': event.image.url if event.image else None,
                    'description': event.description,
                    'start_date': str(event.start_date),
                    'end_date': str(event.end_date),
                    'price': str(event.price),
                    'quantity': purchase_details['quantity'],
                }
                return redirect('checkout')
    else:
        form = PurchaseForm()

    context = {
        'event': event,
        'form': form,
        'tickets': tickets,
        'remaining_seats': remaining_seats,
        'is_organizer': 'is_organizer'
    }
    return render(request, 'GoTickets/event_by_id.html', context)



@login_required
def checkout(request):
    event_details = request.session.get('event_details', {})
    tax = 2
    event_price = float(event_details.get('price', 0))
    quantity = int(event_details.get('quantity', 1))
    total_price = (event_price * quantity) + tax

    if request.method == "POST":
        card = CardForm(request.POST)
        if card.is_valid():
            event = get_object_or_404(Event, id=event_details['id'])
            purchase = Purchase(
                user=request.user,
                event=event,
                quantity=quantity,
                paid=True
            )
            purchase.save()
            request.session['purchase_id'] = purchase.id
            return redirect('order_confirmation')
    else:
        card = CardForm()

    context = {
        'card': card,
        'event': event_details,
        'tax': tax,
        'total_price': total_price,
    }
    return render(request, 'GoTickets/checkout.html', context)





def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {user}')
            return redirect(reverse('login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CreateUserForm()
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

@login_required
def order_confirmation(request):
    purchase_id = request.session.get('purchase_id')
    if not purchase_id:
        return redirect('index')

    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, 'GoTickets/order_confirmation.html', {'purchase': purchase})



@login_required
def account(request):
    user = request.user
    user_profile = user.userprofile

    user_form = UpdateUserForm(instance=user)
    profile_form = UserProfileForm(instance=user_profile)
    password_form = CustomPasswordChangeForm(user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }

    return render(request, 'GoTickets/account.html', context)

@login_required
def update_account_settings(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('account')
        else:
            for form in [user_form, profile_form]:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'GoTickets/account_settings.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in after password change
            messages.success(request, 'Your password has been changed!')
            return redirect('account')
        else:
            for field, errors in password_form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'GoTickets/change_password.html', {
        'password_form': password_form
    })



@login_required
def user_tickets(request):
    now = datetime.now()
    form = FilterForm(request.GET)
    purchase = Purchase.objects.filter(user=request.user)

    if form.is_valid():
        order_type = form.cleaned_data.get('order_type')
        if order_type == 'expired':
            purchase = purchase.filter(end_date__lt=now)
        elif order_type == 'upcoming':
            purchase = purchase.filter(start_date__gte=now)



    tickets_list = Purchase.objects.filter(user=request.user)
    paginator = Paginator(tickets_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'GoTickets/user_tickets.html', {
        'form': form,
        'page_obj': page_obj,
        'ticket_detail_url': reverse('ticket_detailed', kwargs={'id': 0})
    })


@login_required
def user_events(request):
    now = datetime.now()
    form = FilterForm(request.GET)
    events = Event.objects.filter(organizer=request.user)

    if form.is_valid():
        order_type = form.cleaned_data.get('order_type')
        if order_type == 'expired':
            events = events.filter(end_date__lt=now)
        elif order_type == 'upcoming':
            events = events.filter(start_date__gte=now)

    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'GoTickets/user_events.html', {
        'form': form,
        'page_obj': page_obj,
        'event_detail_url_template': reverse('event_by_id', kwargs={'id': 0}),
    })



@login_required
def ticket_detailed(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    qr_img = generate_ticket_qr(id)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_code_base64 = b64encode(buffer.getvalue()).decode('utf-8')
    event = purchase.event
    return render(request, 'GoTickets/ticket_detailed.html', {
        'purchase': purchase,
        'event': event,
        'qr_code_base64': qr_code_base64,
    })


@login_required
def eventcreate(request: HttpRequest):
    upload_form = UploadFileForm()
    event_form = EventForm()

    if request.method == 'POST':
        if 'upload' in request.POST:
            upload_form = UploadFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                events = handle_uploaded_file(request.FILES['file'])
                for event in events:
                    event['organizer_id'] = request.user.id
                request.session['events'] = events
                return render(request, 'GoTickets/confirm_events.html', {'events': events})
            else:
                print(upload_form.errors)
        elif 'create' in request.POST:
            event_form = EventForm(request.POST, request.FILES)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                event.organizer = request.user
                event.save()
                messages.success(request, 'Your event has been posted!')
                return redirect('/event/create/')
            else:
                print(event_form.errors)

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
                organizer_id = event.pop('organizer_id', None)
                if organizer_id:
                    Event.objects.create(**event, organizer_id=organizer_id)
            del request.session['events']
            return redirect('/events/')
        else:
            request.session.pop('events', None)
            return redirect('/upload/')

    return redirect('/upload/')


def generate_ticket_qr(ticket_id):
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add data to the QR code
    qr.add_data(f'Ticket ID: {ticket_id}')
    qr.make(fit=True)

    # Create an image from the QR code instance
    img = qr.make_image(fill='black', back_color='white')
    return img

def download_ticket_pdf(request, event_id, purchase_id):
    event = get_object_or_404(Event, pk=event_id)
    purchase = get_object_or_404(Purchase, pk=purchase_id, event=event, user=request.user)

    qr_img = generate_ticket_qr(event_id)  # Get QR code as an image object
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = ImageReader(buffer)  # Convert the BytesIO stream to ImageReader

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{event.title}-ticket.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, height - 72, event.title)
    if event.image:
        p.drawImage(event.image.path, 72, height - 200, width=200, height=100)

    p.drawImage(qr_image, 280, height - 200, width=100, height=100)  # Use ImageReader object for QR code

    p.setFont("Helvetica", 12)
    p.drawString(72, height - 240, "Location: " + event.location_venue)
    p.drawString(72, height - 260, "Starts: " + event.start_date.strftime('%Y-%m-%d'))
    p.drawString(72, height - 280, "Ends: " + event.end_date.strftime('%Y-%m-%d'))
    p.drawString(72, height - 300, f"Price: ${event.price}")
    p.drawString(72, height - 340, f"Quantity: {purchase.quantity}")
    p.drawString(72, height - 360, "Purchased on: " + purchase.purchase_date.strftime('%Y-%m-%d %H:%M'))

    p.showPage()
    p.save()

    return response




@login_required
def create_ticket(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user != event.organizer:
        raise PermissionDenied("You are not allowed to edit this event.")
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
        else:
            messages.error(request, 'There was an error creating the ticket.')
            print(form.errors)
    else:
        form = TicketForm()

    return render(request, 'GoTickets/createticket.html', {'form': form, 'event': event})
