
from django.shortcuts import render, redirect
from .forms import DonationForm
from django.contrib import messages
from .forms import DonationForm
from .models import Donation
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
import uuid
from django.conf import settings
import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now, timezone
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags

from paypal.standard.forms import PayPalPaymentsForm

from .forms import DonationForm
from .models import Donation, ContactMessage, Subscriber, BlogPost, Project, Event

# Create your views here.
def index(request):
    projects = Project.objects.all()
    events = Event.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:2]
    blog_posts = BlogPost.objects.order_by('-published_date')[:3]
    return render(request, 'core/index.html', {
        'projects': projects,
        'events': events,
        'blog_posts': blog_posts,
    })


def donate_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = Donation(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data['payment_method'],
                proof=form.cleaned_data.get('proof'),
                status='pending',
            )
            donation.save()

            if donation.payment_method == 'paypal':
                request.session['donation_data'] = {
                    'name': donation.name,
                    'email': donation.email,
                    'amount': float(donation.amount),
                    'message': donation.message,
                }
                return redirect('process_payment', donation_id=donation.id)

            messages.success(request, "Thank you for your donation! We will process it shortly.")
            return redirect('donate')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonationForm()
    return render(request, 'core/donate.html', {'form': form})

def donation_success(request):
    data = request.session.get('donation_data')
    if data:
        Donation.objects.create(
            name=data['name'],
            email=data['email'],
            amount=data['amount'],
            message=data['message'],
            payment_status='Completed'
        )
        messages.success(request, "Thank you! Your donation was successful.")
        del request.session['donation_data']
    return redirect('donate')

def donation_cancelled(request):
    messages.warning(request, "Donation was cancelled.")
    return redirect('donate')

def process_payment(request, donation_id):
    donation = Donation.objects.get(id=donation_id)
    paypal_dict = {
    "business": settings.PAYPAL_RECEIVER_EMAIL,
    "amount": str(float(donation.amount)),  # as string
    "item_name": f"Donation from {donation.name}",
    "invoice": str(donation.id),  # as string, must be unique
    "currency_code": "USD",
    "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
    "return_url": request.build_absolute_uri(reverse('donation_success')),
    "cancel_return": request.build_absolute_uri(reverse('donation_cancelled')),
}


    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "core/process_payment.html", {"form": form, "donation": donation})

 #Contact
@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not (name and email and message):
            messages.error(request, 'Please fill in all fields.')
            return redirect('home')

        ContactMessage.objects.create(name=name, email=email, message=message)

        admin_html = render_to_string('emails/admin_message.html', {
            'name': name,
            'email': email,
            'message': message,
        })

        admin_msg = EmailMultiAlternatives(
            subject=f'New Contact Message from {name}',
            body='',
            from_email=f'{name} <{email}>',
            to=[settings.CONTACT_NOTIFY_EMAIL],
            reply_to=[email]
        )
        admin_msg.attach_alternative(admin_html, 'text/html')
        admin_msg.send()

        user_html = render_to_string('emails/user_autoresponse.html', {'name': name})
        user_msg = EmailMultiAlternatives(
            subject='Thank You for Contacting Pravic',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        user_msg.attach_alternative(user_html, 'text/html')
        user_msg.send()

        messages.success(request, 'Your message was sent successfully!')
        return redirect('index')
    return redirect('index')

# Subscribe to Newsletter
@require_http_methods(["POST"])
def subscribe(request):
    email = request.POST.get('email')
    if not Subscriber.objects.filter(email=email).exists():
        Subscriber.objects.create(email=email)

        html_content = render_to_string('emails/email_confirmation.html', {
            'user': {'username': email.split('@')[0]},
            'current_year': now().year
        })

        email_msg = EmailMessage(
            subject="You're now subscribed to our newsletter!",
            body=html_content,
            to=[email]
        )
        email_msg.content_subtype = 'html'
        email_msg.send()

        messages.success(request, "Thank you for subscribing to our newsletter!")
    else:
        messages.info(request, "You are already subscribed.")
    return redirect('index')

@require_http_methods(["GET"])
def blog(request):
    blog_posts = BlogPost.objects.order_by('-published_date')
    return render(request, 'core/blog.html', {'blog_posts': blog_posts})

@require_http_methods(["GET"])
def blog_post_detail(request, slug):
    blog_post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'core/blog_post_detail.html', {'blog_post': blog_post})

@require_http_methods(["GET"])
def projects(request):
    projects = Project.objects.all()
    return render(request, 'core/projects.html', {'projects': projects})

@require_http_methods(["GET"])
def events(request):
    events_list = Event.objects.all().order_by('event_date')
    paginator = Paginator(events_list, 10)  # Show 10 events per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # handles invalid page numbers automatically

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'core/events.html', context)