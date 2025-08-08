from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from datetime import timedelta
import uuid
from django.contrib.auth.models import User
from django_countries.fields import CountryField

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
    proof = models.FileField(upload_to='media/donation_proofs/', null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    country = CountryField(blank_label='(select country)', null=True, blank=True)

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
    featured_image = models.ImageField(upload_to='media/blog/', null=True, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, default='Shoko')

    def __str__(self):
        return self.title    

 #----Project--#
class Project(models.Model):
    CATEGORY_CHOICES = [
        ('Education', 'Education'),
        ('Health', 'Health'),
        ('Entrepreneurship', 'Entrepreneurship'),
        ('Community Development', 'Community Development'),
        ('Technology', 'Technology'),
        ('Environment', 'Environment'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]

    DURATION_UNITS = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]


    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Education')
    description = models.TextField(default='description')
    requirements = models.TextField(blank=True,)
    benefits = models.TextField(blank=True)
    image = models.ImageField(upload_to='media/projects/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    duration = models.PositiveIntegerField(blank=True, null=True)  # e.g. 6
    duration_unit = models.CharField(max_length=10, choices=DURATION_UNITS, blank=True, null=True)  # e.g. 'weeks'
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    location = models.TextField(blank=True, null=True)  # "Virtual - Zoom", "Physical - Harare, Zimbabwe"
    team_members = models.ManyToManyField(User, related_name='projects', blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_projects')

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

    def __str__(self):
        return self.title


class ProjectApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='applications')
    motivation = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('user', 'project')  # Prevent duplicate applications

    def __str__(self):
        return f"{self.user.username} applied to {self.project.title}"
    
class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.project.title}"
    
#----EVENT----#
from django.db import models
from django.utils import timezone

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('live', 'Live'),
        ('online', 'Online'),
        ('in_person', 'In-Person'),
        ('hybrid', 'Hybrid'),
    ]

    EVENT_CATEGORY_CHOICES = [
        ('podcast', 'Podcast'),
        ('webinar', 'Webinar'),
        ('workshop', 'Workshop'),
        ('talk', 'Talk Show'),
        ('watch_party', 'Watch Party'),
        ('class', 'Live Class'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateField()
    event_image = models.ImageField(upload_to='media/events/', null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='live')
    category = models.CharField(max_length=20, choices=EVENT_CATEGORY_CHOICES, default='other')
    url = models.URLField(blank=True, null=True)
    
    def days_until(self):
        """Return number of days from today until the event_date."""
        today = timezone.now().date()
        delta = self.event_date - today
        return delta.days if delta.days >= 0 else 0

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    def __str__(self):
        return self.title
    

class ApplicationImage(models.Model):
    application = models.ForeignKey(ProjectApplication, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='application_images/')

class Task(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.project.title})"    
    

class ChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"

class TaskNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_as_read(self):
        self.is_read = True
        self.save()


