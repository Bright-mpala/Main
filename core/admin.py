from django.contrib import admin
from .models import Donation, ContactMessage, Subscriber, BlogPost, Project, Event, Task
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'author')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    list_filter = ('published_date',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'amount', 'payment_method', 'payment_status', 'created_at',)
    list_filter = ('payment_method', 'payment_status', 'created_at')
    search_fields = ('name', 'email', 'ecocash_transaction_id')

    actions = ['mark_as_verified', 'mark_as_rejected']

    def mark_as_verified(self, request, queryset):
        for donation in queryset:
            if donation.payment_status != 'verified':
                donation.payment_status = 'verified'
                donation.save()

                # Send verification email
                subject = "Your Donation Has Been Verified"
                context = {
                    'name': donation.name,
                    'amount': donation.amount,
                    'project': donation.project.name if donation.project else "General Donation"
                }

                html_content = render_to_string('emails/donation_verified.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [donation.email],
                )
                email.attach_alternative(html_content, "text/html")

                try:
                    email.send()
                except Exception as e:
                    logger.error(f"Error sending verified email to {donation.email}: {e}")

        self.message_user(request, "Selected donations marked as verified and donors notified.")
    mark_as_verified.short_description = "Mark selected donations as Verified"

    def mark_as_rejected(self, request, queryset):
        for donation in queryset:
            if donation.payment_status != 'rejected':
                donation.payment_status = 'rejected'
                donation.save()

                # Send rejection email
                subject = "Your Donation Could Not Be Verified"
                context = {
                    'name': donation.name,
                    'amount': donation.amount,
                    'reason': "Missing or invalid proof of payment."  # You can customize this
                }

                html_content = render_to_string('emails/donation_rejected.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [donation.email],
                )
                email.attach_alternative(html_content, "text/html")

                try:
                    email.send()
                except Exception as e:
                    logger.error(f"Error sending rejection email to {donation.email}: {e}")

        self.message_user(request, "Selected donations marked as rejected and donors notified.")
    mark_as_rejected.short_description = "Mark selected donations as Rejected"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'responded', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('responded', 'created_at')
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'event_type', 'category', 'location')
    list_filter = ('event_type', 'category', 'event_date')
    search_fields = ('title', 'description', 'location')

    def days_until_display(self, obj):
        return obj.days_until()
    days_until_display.short_description = 'Days Until Event'    



from .models import ProjectApplication

admin.site.register(ProjectApplication)   
admin.site.register(Task)   