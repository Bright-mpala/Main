from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

class CounselingType(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} (${self.price})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    counseling_type = models.ForeignKey(CounselingType, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.counseling_type.name} on {self.date} at {self.time}"
    
from django.db import models

class CounselingSiteSettings(models.Model):
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Counseling Site Approved: {self.approved}"

    class Meta:
        verbose_name = "Counseling Site Setting"
        verbose_name_plural = "Counseling Site Settings"    

@receiver(post_save, sender=Booking)
def send_booking_confirmation_email(sender, instance, created, **kwargs):
    if created:
        subject = "Counseling Appointment Booked"
        message = (
            f"Hello {instance.user.username},\n\n"
            f"Your counseling session has been booked for {instance.date} at {instance.time}.\n\n"
            f"We will notify you once it's approved.\n\nThank you."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=False
        )        

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username}'