import pytz

from django.utils import timezone


class TimezoneMiddleware(object):
    def process_request(self, request):
        tzname = request.session.get('django_timezone', None)
        if tzname:
            timezone.activate(pytz.timezone(tzname))
            return
        else:
            if request.user.is_authenticated():
                try:
                    user_tz = request.user.userprofile.area_city.timezone
                except Exception:
                    pass
                else:
                    if user_tz:
                        timezone.activate(pytz.timezone(user_tz))
                        request.session['django_timezone'] = user_tz
                        return
        timezone.deactivate()
