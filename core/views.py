from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, FormView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .forms import DonationForm, ProjectApplicationForm, ProjectCommentForm, TaskForm
from .models import (
    Donation, ContactMessage, Subscriber, BlogPost, Project, Event,
    ProjectApplication, ApplicationImage, ProjectComment, Task,
    ChatMessage, TaskNotification
)

def index(request):
    featured_projects = Project.objects.order_by('-created_at')[:2]
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:2]
    recent_blog_posts = BlogPost.objects.order_by('-published_date')[:3]
    categories = Project.CATEGORY_CHOICES
    projects_per_category = {category: Project.objects.filter(category=category).count() for category, _ in categories}

    context = {
        'featured_projects': featured_projects,
        'events': upcoming_events,
        'blog_posts': recent_blog_posts,
        'projects_per_category': projects_per_category,
        'total_projects': Project.objects.count(),
    }
    return render(request, 'core/index.html', context)


def donate_view(request):
    projects = Project.objects.filter(status='ongoing')  # Only show ongoing projects

    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.status = 'pending'
            donation.save()

            messages.success(request, f"Thank you for your donation, {donation.name}! "
                                      f"{'You have supported ' + donation.project.title if donation.project else 'You made a general donation.'}")

            if donation.payment_method == 'paypal':
                request.session['donation_data'] = {
                    'name': donation.name,
                    'email': donation.email,
                    'amount': float(donation.amount),
                    'message': donation.message,
                    'project_id': donation.project.id if donation.project else None,
                }
                return redirect('process_payment', donation_id=donation.id)

           
        else:
            messages.error(request, "Please correct the errors below.")
            return redirect('donate')
    else:
        form = DonationForm()

    return render(request, 'core/donate.html', {'form': form, 'projects': projects})


def donation_success(request):
    data = request.session.get('donation_data')
    if data:
        # Create donation record
        donation = Donation.objects.create(
            name=data['name'],
            email=data['email'],
            amount=data['amount'],
            message=data.get('message', ''),
            status='completed'  # Use correct field name
        )

        # Send thank-you email
        if donation.project:
            project_line = f"You supported the project: {donation.project.title}."
        else:
            project_line = "You made a general donation."

        subject = "Thank You for Your Donation"
        message = f"Dear {donation.name},\n\n" \
                  f"Thank you for your donation of ${donation.amount}.\n" \
                  f"{project_line}\n\n" \
                  f"We truly appreciate your support!\n\nBest regards,\nThe Team"

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [donation.email])

        # Clear the session
        del request.session['donation_data']

    return redirect('donate')

def donation_cancelled(request):
    messages.warning(request, "Donation was cancelled.")
    return redirect('donate')


def process_payment(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": str(float(donation.amount)),
        "item_name": f"Donation from {donation.name}",
        "invoice": str(donation.id),
        "currency_code": "USD",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('donation_success')),
        "cancel_return": request.build_absolute_uri(reverse('donation_cancelled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "core/process_payment.html", {"form": form, "donation": donation})


@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not (name and email and message):
            messages.error(request, 'Please fill in all fields.')
            return redirect('index')

        ContactMessage.objects.create(name=name, email=email, message=message)

        # Email admin notification
        admin_html = render_to_string('emails/admin_message.html', {'name': name, 'email': email, 'message': message})
        admin_msg = EmailMultiAlternatives(
            subject=f'New Contact Message from {name}',
            body='',
            from_email=f'{name} <{email}>',
            to=[settings.CONTACT_NOTIFY_EMAIL],
            reply_to=[email]
        )
        admin_msg.attach_alternative(admin_html, 'text/html')
        admin_msg.send()

        # Auto response to user
        user_html = render_to_string('emails/user_autoresponse.html', {'name': name})
        user_msg = EmailMultiAlternatives(
            subject='Thank You for Contacting DR SHOKO',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        user_msg.attach_alternative(user_html, 'text/html')
        user_msg.send()

        messages.success(request, 'Your message was sent successfully!')
        return redirect('index')
    return redirect('index')


@require_http_methods(["POST"])
def subscribe(request):
    email = request.POST.get('email')
    if email and not Subscriber.objects.filter(email=email).exists():
        Subscriber.objects.create(email=email)

        html_content = render_to_string('emails/email_confirmation.html', {
            'user': {'username': email.split('@')[0]},
            'current_year': timezone.now().year
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
        messages.info(request, "You are already subscribed or email invalid.")
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
    category = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()

    projects = Project.objects.all()

    if category:
        projects = projects.filter(category=category)

    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(benefits__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )

    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Project.CATEGORY_CHOICES
    context = {
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': category,
    }
    return render(request, 'core/projects.html', context)


@require_http_methods(["GET"])
def events(request):
    events_list = Event.objects.all().order_by('event_date')
    paginator = Paginator(events_list, 10)
    today = timezone.now().date()
    upcoming_events = Event.objects.filter( event_date__gte=today).order_by('event_date')
    past_events = Event.objects.filter(event_date__lt=today).order_by('-event_date')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'core/events.html', context)


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'core/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        project = self.get_object()

        if user.is_authenticated:
            context['user_comment_count'] = project.comments.filter(user=user).count()
            context['has_applied'] = ProjectApplication.objects.filter(user=user, project=project).exists()
        else:
            context['user_comment_count'] = 0
            context['has_applied'] = False

        context['form'] = ProjectApplicationForm()
        context['comment_form'] = ProjectCommentForm()
        context['comments'] = project.comments.order_by('-created_at')
        context['applications'] = project.applications.all() if project.owner == user else None
        return context


@method_decorator(login_required, name='dispatch')
class ProjectCommentView(FormView):
    form_class = ProjectCommentForm

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        comment.project = project
        comment.user = self.request.user
        comment.save()

        messages.success(self.request, "Comment posted.")

        # Create notification if project owner is different from commenter
        if project.owner and project.owner != self.request.user:
            message = f"{comment.user.username} commented on your project '{project.title}'."
            TaskNotification.objects.create(
                user=project.owner,
                project=project,
                message=message,
                is_read=False
            )

            # Send notification live over channels
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f'notify_{project.owner.id}',
                {
                    'type': 'notify',
                    'message': message,
                }
            )

        return redirect('project_detail', pk=project.pk)

@method_decorator(login_required, name='dispatch')
class ProjectApplyView(FormView):
    form_class = ProjectApplicationForm  
    template_name = 'core/project_apply.html'  
    success_url = '/projects/'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        user = self.request.user

        if ProjectApplication.objects.filter(user=user, project=project).exists():
            messages.info(self.request, 'You have already applied to this project.')
            return redirect('project_detail', pk=project.pk)

        application = form.save(commit=False)
        application.user = user
        application.project = project
        application.save()

        images = self.request.FILES.getlist('images')
        for image in images:
            ApplicationImage.objects.create(application=application, image=image)

        if project.owner and project.owner.email:
            send_mail(
                subject="New Project Application",
                message=f"{user.username} has applied for {project.title}.",
                from_email=None,
                recipient_list=[project.owner.email],
                fail_silently=True
            )

        messages.success(self.request, 'Application submitted successfully!')
        return redirect('project_detail', pk=project.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context


@staff_member_required
@require_POST
def update_application_status(request, pk, status):
    application = get_object_or_404(ProjectApplication, pk=pk)
    if status not in ['approved', 'rejected']:
        return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)

    application.status = status
    application.save()

    subject = f"Your application for {application.project.title} has been {status}"
    message = render_to_string('emails/application_status.html', {
        'user': application.user,
        'project': application.project,
        'status': status,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [application.user.email], fail_silently=False)

    return JsonResponse({'success': True, 'message': f'Application {status} and email sent.'})


@login_required
def project_workspace(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user

    is_member = (
        user == project.owner or
        project.team_members.filter(id=user.id).exists() or
        ProjectApplication.objects.filter(project=project, user=user, status='approved').exists()
    )
    if not is_member:
        return HttpResponseForbidden("Not authorized")

    user_tasks = Task.objects.filter(project=project, assigned_to=user).order_by('-created_at')
    notifications = TaskNotification.objects.filter(user=user, project=project).order_by('-created_at')[:10]
    chat_messages = project.chat_messages.select_related('user').all()

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        msg = request.POST.get('message', '').strip()
        if not msg:
            return JsonResponse({'success': False, 'message': 'Empty message'}, status=400)

        try:
            chat_msg = ChatMessage.objects.create(project=project, user=user, message=msg)
            return JsonResponse({
                'success': True,
                'message': 'Message sent',
                'username': user.username,
                'message_text': chat_msg.message,
                'created_at': chat_msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

    context = {
        'project': project,
        'user_tasks': user_tasks,
        'notifications': notifications,
        'chat_messages': chat_messages,
    }
    return render(request, 'core/project_workspace.html', context)


@login_required
def project_workspace_list(request):
    user = request.user
    approved_apps = ProjectApplication.objects.filter(user=user, status='approved').select_related('project')
    projects_from_apps = [app.project for app in approved_apps]
    owned_projects = Project.objects.filter(owner=user)
    projects = list(set(projects_from_apps) | set(owned_projects))

    return render(request, 'core/project_workspace_list.html', {'projects': projects})


@require_POST
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user

    # Only the assigned user or the project owner can mark as complete
    if task.assigned_to != user and task.project.owner != user:
        return JsonResponse({'success': False, 'message': 'Not authorized'}, status=403)

    task.completed = True
    task.save()

    # Notify channels group about task completion
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'task_{task.project.id}',
        {
            'type': 'send_task',
            'task_id': task.id,
            'title': task.title,
            'completed': True,
        }
    )

    # Notify the assigned user (if different)
    async_to_sync(channel_layer.group_send)(
        f'notify_{task.assigned_to.id}',
        {
            'type': 'notify',
            'message': f"Task '{task.title}' completed"
        }
    )

    # Create notification object
    TaskNotification.objects.create(
        user=task.assigned_to,
        project=task.project,
        message=f"Task '{task.title}' marked as completed by {user.username}",
        is_read=False
    )

    # Optional email notification
    if task.assigned_to.email:
        send_mail(
            subject="Task Completed",
            message=f"The task '{task.title}' has been marked as completed in project '{task.project.title}'.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assigned_to.email],
            fail_silently=True,
        )

    return JsonResponse({'success': True, 'message': 'Task marked as complete'})


@require_POST
@login_required
def mark_notification_read(request):
    notification_id = request.POST.get('id')
    try:
        notification = TaskNotification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except TaskNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})