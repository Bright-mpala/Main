from .models import ProjectApplication

def approved_projects_count(request):
    user = request.user
    if user.is_authenticated:
        count = ProjectApplication.objects.filter(user=user, status='approved').count()
        return {'approved_projects_count': count}
    return {'approved_projects_count': 0}
