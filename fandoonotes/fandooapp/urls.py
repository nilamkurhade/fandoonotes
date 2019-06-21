from django.conf.urls import url
from fandooapp import views
from django.conf.urls import url, include


# SET THE NAMESPACE!
app_name = 'fandooapp'

# Be careful setting the name to just /login use userlogin instead!
# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
     url(r'^user_login/$', views.user_login, name='user_login'),
     url(r'^signup/$', views.signup, name='signup'),


]
