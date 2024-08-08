from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Event, Purchase, Card, Ticket
from django.utils.text import slugify
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UpdateUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'location_country', 'address',
            'location_venue', 'start_date', 'end_date', 'image',
            'price', 'seats', 'age_restriction', 'category'
        ]

class UpdateEventForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['quantity']


class SearchForm(forms.Form):
    query = forms.CharField()
    from_date = forms.DateField(label='From', widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])
    to_date = forms.DateField(label='To', widget=forms.DateInput(format='%d/%m/%Y'), input_formats=['%d/%m/%Y'])

    def clean(self):
        # Call the parent clean method to perform the default validation
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        if from_date and to_date:
            if from_date > to_date:
                raise ValidationError({
                    'from_date': _('Start date cannot be after end date.'),
                    'to_date': _('End date cannot be before start date.')
                })
        return cleaned_data

    def __str__(self):
        return self.title


class SearchEventForm(forms.Form):
    query = forms.CharField()


class UploadFileForm(forms.Form):
    file = forms.FileField()

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = '__all__'

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'placeholder': 'Enter your current password'
        })
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'placeholder': 'Enter a new password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'placeholder': 'Re-enter the new password'
        })
    )


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'price', 'number_of_tickets']



class FilterForm(forms.Form):
    ORDER_TYPE_CHOICES = [
    ('', 'All events'),
    ('expired', 'Expired'),
    ('upcoming', 'Upcoming'),
]

    order_type = forms.ChoiceField(
        choices=ORDER_TYPE_CHOICES,
        required=True,
    )
