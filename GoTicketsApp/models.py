from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=80)
    organizer = models.ForeignKey(User, null=True, blank = True, on_delete=models.CASCADE, related_name= 'organizer' )
    description = models.TextField()
    location = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='images/')
    price = models.DecimalField(max_digits=6, decimal_places=2)


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    vip = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    purchase_date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

class Card(models.Model):
    card_number = models.CharField(max_length=16)
    date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3)
