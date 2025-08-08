from django.contrib import admin
from .models import Booking, CounselingType, CounselingSiteSettings, Notification
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'counseling_type', 'date', 'time', 'approved')
    list_filter = ('approved', 'counseling_type')
    actions = ['approve_bookings']

    def approve_bookings(self, request, queryset):
        for booking in queryset:
            if not booking.approved:
                booking.approved = True
                booking.save()

                # Send approval email
                subject = "Your Counseling Session is Approved"
                context = {
                    'user': booking.user,
                    'date': booking.date,
                    'time': booking.time.strftime('%H:%M'),
                    'site_name': 'Your Counseling Platform',
                }

                html_content = render_to_string('emails/approved_email.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.user.email],
                )
                email.attach_alternative(html_content, "text/html")
                try:
                    email.send()
                except Exception as e:
                    logger.error(f"Error sending approval email: {e}")

        self.message_user(request, "Selected bookings have been approved and users notified.")
    approve_bookings.short_description = 'Approve selected bookings and notify users'

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Booking.objects.get(pk=obj.pk)
            super().save_model(request, obj, form, change)
            updated_obj = Booking.objects.get(pk=obj.pk)

            # Approval email if approved now
            if not old_obj.approved and updated_obj.approved:
                subject = 'Booking Approved'
                context = {
                    'user': updated_obj.user,
                    'date': updated_obj.date,
                    'time': updated_obj.time.strftime('%H:%M'),
                }
                html_content = render_to_string('emails/approved_email.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [updated_obj.user.email],
                )
                email.attach_alternative(html_content, "text/html")
                try:
                    email.send()
                except Exception as e:
                    logger.error(f"Error sending approval email: {e}")

            # Reschedule email
            elif old_obj.date != updated_obj.date or old_obj.time != updated_obj.time:
                subject = "Your Counseling Session Has Been Rescheduled"
                context = {
                    'user': updated_obj.user,
                    'new_date': updated_obj.date,
                    'new_time': updated_obj.time.strftime('%H:%M'),
                    'confirm_url': request.build_absolute_uri(
                        reverse('counseling:confirm_booking', args=[updated_obj.pk])
                    )
                }

                html_content = render_to_string('emails/reschedule_email.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [updated_obj.user.email],
                )
                email.attach_alternative(html_content, "text/html")
                try:
                    email.send()
                except Exception as e:
                    logger.error(f"Error sending reschedule email: {e}")
        else:
            super().save_model(request, obj, form, change)

admin.site.register(CounselingType)

@admin.register(CounselingSiteSettings)
class CounselingSiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('approved',)

def notify_admin_of_booking(booking):
    admin_user = get_user_model().objects.filter(is_superuser=True).first()
    subject = f'New Booking from {booking.user.get_full_name()}'
    message = f"""
    A new counseling appointment has been booked:

    Name: {booking.user.get_full_name()}
    Date: {booking.date}
    Time: {booking.time}
    Type: {booking.counseling_type}

    Please review and approve the booking.
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
    Notification.objects.create(
      user=admin_user,
     message=f"New booking submitted by {booking.user.get_full_name()} on {booking.date} at {booking.time}."
    )