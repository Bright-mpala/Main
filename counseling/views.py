from django.views.generic import CreateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from .models import Booking, CounselingType, CounselingSiteSettings, Notification
from .forms import BookingForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_date, parse_time
from django.conf import settings
from django.views import View
from .admin import notify_admin_of_booking
from django.shortcuts import render
from datetime import datetime
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def counselling_home(request):
   return render(request, 'counseling/counseling_home.html', {'year': datetime.now().year})
   

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'counseling/book.html'
    success_url = '/counseling/all-bookings/'  # or use reverse_lazy
    login_url = '/accounts/login/'

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Check if user has 3 or more future bookings
        user_booking_count = Booking.objects.filter(
            user=self.request.user,
            date__gte=timezone.now().date()
        ).count()

        if user_booking_count >= 3:
            messages.error(self.request, "You can only have up to 3 active bookings.")
            return redirect('counseling:all_bookings')  # make sure this matches your url name

        # Save the booking
        response = super().form_valid(form)
        booking = self.object

        # Send confirmation email
        try:
            send_mail(
                subject="Counseling Appointment Booked",
                message=(
                    f"Hello {self.request.user.username},\n\n"
                    f"Your counseling session has been booked for {booking.date} at {booking.time}.\n\n"
                    f"We will notify you once it's approved.\n\nThank you."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")

        messages.success(self.request, 'Your booking request was sent successfully! Await admin approval.')

        # Notify admin (optional function)
        notify_admin_of_booking(booking)

        return response
    


@require_GET
def check_availability(request):
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    date = parse_date(date_str)
    time = parse_time(time_str)

    if not date or not time:
        return JsonResponse({'available': False, 'error': 'Invalid date or time'}, status=400)

    exists = Booking.objects.filter(date=date, time=time, approved=True).exists()
    return JsonResponse({'available': not exists})

from django.contrib.auth.mixins import LoginRequiredMixin

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'counseling/booking_list.html'
    context_object_name = 'bookings'

  
    def get_queryset(self):
        filter_option = self.request.GET.get('filter', 'upcoming')
        now = timezone.now().date()
        if filter_option == 'past':
            return Booking.objects.filter(user=self.request.user, date__lt=now)
        return Booking.objects.filter(user=self.request.user, date__gte=now)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'upcoming')
        return context


class CounselingNotAvailableView(TemplateView):
    template_name = 'counseling/not_available.html'


class ConfirmBookingView(LoginRequiredMixin, View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)
        # Here, you could mark the booking as confirmed (add a field if needed)
        messages.success(request, "Thank you for confirming your appointment!")
        return redirect('counseling:my_bookings')


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class RescheduleBookingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        new_date = request.POST.get('date')
        new_time = request.POST.get('time')

        if new_date and new_time:
            booking.date = new_date
            booking.time = new_time
            booking.approved = False  # Reset approval
            booking.save()

            messages.success(request, 'Your booking has been rescheduled and awaits approval.')
            return redirect('counseling:all-bookings')
        
        return JsonResponse({'success': False, 'error': 'Invalid date or time'})

@require_POST
@login_required
def delete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    messages.success(request, "Booking deleted.")
    return redirect('counseling:all-bookings')
