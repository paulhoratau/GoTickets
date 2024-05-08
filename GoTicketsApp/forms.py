from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Event, Purchase

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields =  ['title', 'description', 'location', 'start_date', 'end_date', 'image', 'price']

class UpdateEventForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['vip', 'quantity']

class SearchForm(forms.Form):
    query = forms.CharField()

class UploadFileForm(forms.Form):
    file = forms.FileField()
