from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils import timezone
from .models import BlogPost, Project, Subscriber
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=BlogPost)
def send_blog_notification(sender, instance, created, **kwargs):
    if created:
        subscribers = Subscriber.objects.filter(subscribed=True)
        recipient_list = [sub.email for sub in subscribers]
        if not recipient_list:
            return

        html_content = render_to_string('emails/new_blog.html', {
            'blog': instance,
            'current_year': timezone.now().year,
        })

        email = EmailMessage(
            subject=f"📰 New Blog Post: {instance.title}",
            body=html_content,
            to=[],
            bcc=recipient_list,
        )
        email.content_subtype = 'html'
        try:
            email.send(fail_silently=False)
            logger.info(f"Sent new blog notification to {len(recipient_list)} subscribers.")
        except Exception as e:
            logger.error(f"Error sending blog notification email: {e}")


@receiver(post_save, sender=Project)
def send_project_notification(sender, instance, created, **kwargs):
    if created:
        subscribers = Subscriber.objects.filter(subscribed=True)
        recipient_list = [sub.email for sub in subscribers]

        if not recipient_list:
            return

        html_content = render_to_string('emails/new_project.html', {
            'project': instance,
            'current_year': timezone.now().year,
        })

        email = EmailMessage(
            subject=f"📢 New Project: {instance.title}",
            body=html_content,
            to=[],
            bcc=recipient_list,
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)
