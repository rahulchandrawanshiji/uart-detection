# simple_ui_project/middleware.py

from django.contrib.auth import get_user_model, login

class AutoLoginAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            print("Client IP:", request.META.get('REMOTE_ADDR'))  # For debugging
            if not request.user.is_authenticated:
                User = get_user_model()
                try:
                    user = User.objects.get(username='pi')  # Replace with your username
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                except User.DoesNotExist:
                    print("User 'pi' not found!")
        response = self.get_response(request)
        return response
