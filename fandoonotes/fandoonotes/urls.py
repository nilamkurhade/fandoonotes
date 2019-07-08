"""fandoonotes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from fandooapp import views

# urls

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    path('fandooapp/', include('django.contrib.auth.urls')),
    url(r'^index/$', views.index, name='index'),
    url(r'^special/', views.special, name='special'),
    url(r'^fandooapp/', include('fandooapp.urls')),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),     # <--
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^upload/$', views.s3_upload, name='upload'),
    path('notes/', views.NotesList.as_view()),
    path('labels/', views.LabelList.as_view()),
    path('label/<int:id>/', views.LabelViewDetails.as_view()),
    path('note/<int:id>/', views.Notedata.as_view()),
    path('trash/', views.NoteTrashView.as_view()),
    path('archive/', views.NoteArchiveview.as_view()),
    path('reminder/', views.NoteReminderview.as_view()),
]
