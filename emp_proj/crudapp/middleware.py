from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

EXEMPT_PATHS = ['/login/', '/', '/session-expired/', '/logout/']

class SessionIdleTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('emp_id'):
            if request.path not in EXEMPT_PATHS:

                login_time = request.session.get('login_time')
                timeout = getattr(settings, 'SESSION_TIMEOUT', 3600)  # default 1 hr

                if login_time:
                    logged_in_at = timezone.datetime.fromisoformat(login_time)

                    if timezone.is_naive(logged_in_at):
                        logged_in_at = timezone.make_aware(logged_in_at)

                    elapsed = (timezone.now() - logged_in_at).total_seconds()

                    if elapsed > timeout:
                        # Clear LoggedInUser record
                        from crudapp.models import EmpDetail, LoggedInUser
                        try:
                            emp = EmpDetail.objects.get(emp_id=request.session.get('emp_id'))
                            LoggedInUser.objects.filter(emp=emp).update(session_key=None)
                        except EmpDetail.DoesNotExist:
                            pass
                    
                        request.session.flush()
                        return redirect('session_expired')

        return self.get_response(request)