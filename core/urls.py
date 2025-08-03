from django.urls import path
from core import views
from django.views.generic import TemplateView

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

]