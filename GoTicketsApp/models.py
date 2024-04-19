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
