from django.contrib import admin
from .models import Donation, ContactMessage, Subscriber, BlogPost, Project, Event
from django.utils.html import format_html
from django.utils.safestring import mark_safe


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'author')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    list_filter = ('published_date',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'amount', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'created_at')
    search_fields = ('name', 'email', 'ecocash_transaction_id')

    actions = ['mark_as_verified', 'mark_as_rejected']

    def mark_as_verified(self, request, queryset):
        updated = queryset.update(payment_status='verified')
        self.message_user(request, f"{updated} donation(s) marked as verified.")
    mark_as_verified.short_description = "Mark selected donations as Verified"

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(payment_status='rejected')
        self.message_user(request, f"{updated} donation(s) marked as rejected.")
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
    list_display = ('title', 'event_date', 'days_until_display')
    search_fields = ('title',)
    list_filter = ('event_date',)

    def days_until_display(self, obj):
        return obj.days_until()
    days_until_display.short_description = 'Days Until Event'    