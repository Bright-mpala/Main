from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from datetime import timedelta
import uuid


class Donation(models.Model):
    PAYMENT_CHOICES = [
        ('paypal', 'PayPal'),
        ('ecocash', 'EcoCash'),
        ('bank', 'Bank Transfer'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    ecocash_phone = models.CharField(max_length=15, blank=True, null=True)
    ecocash_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    bank_transfer_proof = models.FileField(upload_to='bank_proofs/', blank=True, null=True)
    proof = models.FileField(upload_to='donation_proofs/', null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.payment_method} - ${self.amount} - {self.payment_status}"


PAYMENT_METHODS = [
    ('bank', 'Bank Transfer'),
    ('ecocash', 'EcoCash'),
    ('paypal', 'PayPal'),
]

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class BlogPost(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    content =  RichTextField()
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, default='Pravic Poultry')

    def __str__(self):
        return self.title    

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)  # Optional link to project
    

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()
    location = models.CharField(max_length=200, blank=True, null=True)

    def days_until(self):
        """Return number of days from today until the event_date."""
        today = timezone.now().date()
        delta = self.event_date - today
        return delta.days if delta.days >= 0 else 0


    def __str__(self):
        return self.title
