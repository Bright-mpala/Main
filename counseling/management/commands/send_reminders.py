from django.core.management.base import BaseCommand
from counseling.models import Booking
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send email reminders 24 hours before appointments'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        tomorrow = now + timedelta(days=1)

        bookings = Booking.objects.filter(
            approved=True,
            date=tomorrow.date(),
            time__hour=tomorrow.hour
        )

        for booking in bookings:
            subject = 'Reminder: Your Counseling Appointment is Tomorrow'
            message = f'Dear {booking.user.first_name},\n\nJust a reminder that your counseling session is scheduled for {booking.date} at {booking.time}.\n\nThank you.'
            recipient = booking.user.email

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
                self.stdout.write(self.style.SUCCESS(f'Reminder sent to {recipient}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error sending to {recipient}: {e}'))
