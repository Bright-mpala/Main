from django.urls import path
from core import views
from django.views.generic import TemplateView
from .views import ProjectDetailView, ProjectApplyView, ProjectCommentView
urlpatterns = [
    path('', views.index, name='index'),
    path('donate/', views.donate_view, name='donate'),
    path('donation-success/', views.donation_success, name='donation_success'),
    path('donate/process/<int:donation_id>/', views.process_payment, name='process_payment'),
    path('donation-cancelled/', views.donation_cancelled, name='donation_cancelled'),
    path("terms/", TemplateView.as_view(template_name="core/terms.html"), name="terms"),
    path('contact/', views.contact_view, name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('events/', views.events, name='events'),
    path('projects/', views.projects, name='projects'),
    path('about/', TemplateView.as_view(template_name="core/about.html"), name='about'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/apply/', ProjectApplyView.as_view(), name='project-apply'),
    path('projects/<int:pk>/comment/', ProjectCommentView.as_view(), name='project-comment'),
    path('application/<int:pk>/<str:status>/', views.update_application_status, name='application-status'),
    path('workspaces/', views.project_workspace_list, name='project_workspace_list'),
    path('workspaces/<int:pk>/', views.project_workspace, name='project_workspace'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),

]