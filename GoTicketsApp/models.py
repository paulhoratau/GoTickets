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

class CartItem(models.Model):
    ticket = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class Cart(models.Model):
    items = models.ManyToManyField(CartItem)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
