from django.http import HttpResponseRedirect, HttpResponse
from .views import user_login
# decorators for login


def myuser_login_required(f):
    def wrap(request, *args, **kwargs):
        # this check the session if userid key exist, if not it will redirect to login page
        if 'username' not in request.session.keys():
            return HttpResponseRedirect("/fandooapp/user_login")
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
