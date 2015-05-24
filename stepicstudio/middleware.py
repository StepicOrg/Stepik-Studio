from django.utils.timezone import now
from stepicstudio.models import UserProfile

class SetLastVisitMiddleware(object):
    def process_response(self, request, response):
        try:
            if request.user.is_authenticated():
            # Update last visit time after request finished processing.
                UserProfile.objects.filter(pk=request.user.pk).update(last_visit=now())
        except Exception as e:
            pass
        return response
