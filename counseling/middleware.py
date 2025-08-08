from django.shortcuts import redirect
from django.urls import reverse
from .models import CounselingSiteSettings

class CounselingAvailabilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [
            reverse('counseling:counseling_not_available'),
        ]
        if request.path.startswith('/counseling/') and request.path not in allowed_paths:
            settings = CounselingSiteSettings.objects.first()
            if not settings or not settings.approved:
                return redirect(reverse('counseling:counseling_not_available'))
        return self.get_response(request)
