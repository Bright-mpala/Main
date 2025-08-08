from django.urls import path
from . import views
from .views import CounselingNotAvailableView, BookingListView, counselling_home, RescheduleBookingView, delete_booking

app_name = 'counselling'

urlpatterns = [
    path('', counselling_home, name='counselling_home'),
    path('book/', views.BookingCreateView.as_view(), name='book'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('not-available/', CounselingNotAvailableView.as_view(), name='counseling_not_available'),
    path('confirm/<int:pk>/', views.ConfirmBookingView.as_view(), name='confirm_booking'),
    path('all-bookings/', BookingListView.as_view(), name='all-bookings'),
    path('reschedule/<int:pk>/', RescheduleBookingView.as_view(), name='reschedule_booking'),
    path('delete-booking/<int:pk>/', delete_booking, name='delete_booking'),

]
