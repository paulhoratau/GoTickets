from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm, EventForm, UpdateEventForm
from .models import Event, User, CartItem, Cart




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
    return render(request, 'GoTickets/events_by_id.html', {'event': event})


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
    orders = Event.objects.all()
    context = {
        'orders': orders
    }
    return render(request, 'GoTickets/order_confirmation.html', context)

def cart_detail(request):
    cart_id = request.session.get("cart_id", None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart()
        cart.save()
        request.session['cart_id'] = cart.id
    return render(request, 'GoTickets/cart_detail.html', {'cart': cart})

def add_to_cart(request, event_id):
    event = Event.objects.get(id=event_id)
    cart_id = request.session.get("cart_id", None)
    cart, created = Cart.objects.get_or_create(id=cart_id)
    if created:
        request.session['cart_id'] = cart.id
    item, created = CartItem.objects.get_or_create(ticket=event, defaults={'quantity': 1})
    if not created:
        item.quantity += 1
        item.save()
    cart.items.add(item)
    cart.total += item.quantity * event.price
    cart.save()
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    item = CartItem.objects.get(id=item_id)
    cart = Cart.objects.get(id=request.session.get("cart_id"))
    cart.total -= item.ticket.price * item.quantity
    cart.items.remove(item)
    item.delete()
    cart.save()
    return redirect('cart_detail')
