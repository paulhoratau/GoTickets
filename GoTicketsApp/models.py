from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Signal to create or update the user profile whenever the User model is saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()



class Event(models.Model):
    AGE_RESTRICTION_CHOICES = [
        ('No', 'No'),
        ('12', '12+'),
        ('14', '14+'),
        ('16', '16+'),
        ('18', '18+'),
        ('21', '21+'),
    ]

    CATEGORY_CHOICES = [
        ('Stand-up Comedy', 'Stand-up Comedy'),
        ('TH', 'Theatre'),
        ('SP', 'Sport'),
        ('CO', 'Concert'),
    ]

    age_restriction = models.CharField(
        max_length=2,
        choices=AGE_RESTRICTION_CHOICES,
        default='No',
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Stand-up Comedy',
    )
    title = models.CharField(max_length=80)
    organizer = models.ForeignKey(User, null=True, blank = True, on_delete=models.CASCADE, related_name= 'organizer' )
    description = models.TextField()
    location_country = models.CharField(max_length=30)
    address = models.CharField(max_length=60)
    location_venue = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='images/')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seats = models.DecimalField(max_digits=6, decimal_places=0)


class Ticket(models.Model):
    event = models.ForeignKey(Event, null=True, blank = True, on_delete=models.CASCADE, related_name= 'event' )
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=6, decimal_places=0)
    number_of_tickets = models.IntegerField(default=1)




class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    purchase_date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

class Card(models.Model):
    card_number = models.CharField(max_length=16)
    date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=3)
    full_name = models.CharField(max_length=30)
 