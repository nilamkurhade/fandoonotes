from fandoonotes.fandoonotes.fandooapp import views
import pytest
from mixer.backend.django import mixer
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from .models import Notes
from .views import LabelList
pytestmark = pytest.mark.django_db


class TestMyModel:
    def test_mymodel(self):
        my_model = mixer.blend("fandooapp.Notes")
        assert my_model.pk == 1, "Should create a Notes instance"


class TestMyView:
    # test case for all notes list
    def test_NotesList(self):
        req = RequestFactory().get(reverse("fandooapp:NotesList"))
        resp = views.NotesList.as_view()(req)
        assert resp.status_code == 200

    # test case for trash view
    def test_trashView(self):
        req = RequestFactory().get(reverse("fandooapp:NoteTrash"))
        resp = views.LabelList.as_view()(req)
        assert resp.status_code == 200

    # test case for
    def test_archiveView(self):
        req = RequestFactory().get(reverse("fandooapp:NoteArchive"))
        resp = views.LabelList.as_view()(req)
        assert resp.status_code == 200


class TestMyCreateView:
    def test_authentication(self):
        req = RequestFactory().get(reverse("fandooapp:NotesList"))
        # req.user = AnonymousUser()
        resp = views.NotesList.as_view()(req)
        assert resp.status_code == 200

    def test_post(self):
        assert False is Notes.objects.all().exists()
        data = {
            "name": "Hans",
            "other_model": mixer.blend("fandooapp.MyOtherModel").pk
        }
        req = RequestFactory().post(reverse("fandooapp:Notedata"), data=data)
        resp = views.NotesList.as_view()(req)
        assert resp.status_code == 302
        assert Notes.objects.all().exists()
        assert Notes.objects.all()[0].name == "note1"


class TestMyUpdateView:
    def test_authentication(self):
        my_model = mixer.blend("fandooapp.Notes")

        req = RequestFactory().get(reverse("fandooapp:Notedata", kwargs={'pk': Notes.pk}))
        req.user = AnonymousUser()
        resp = views.Notedata.as_view()(req, pk=Notes.pk)
        assert resp.status_code == 302, "You have to be logged in"
        assert "login" in resp.url

        req.user = mixer.blend(User)
        resp = views.Notedata.as_view()(req, pk=Notes.pk)
        assert resp.status_code == 200, "Authenticaiton successfull"

    def test_post(self):
        my_model = mixer.blend("fandooapp.Notes", name="Dieter")
        data = {
            "name": "Hans",
            "other_model": my_model.other_model.pk
        }
        req = RequestFactory().post(reverse("fandooapp:Notedata", kwargs={'pk': Notes.pk}), data=data)
        req.user = mixer.blend(User)

        resp = views.Notedata.as_view()(req, pk=my_model.pk)
        assert resp.status_code == 302, "redirect to success url"
        assert "/update_success/" in resp.url
        assert my_model.name == "Dieter"
        my_model.refresh_from_db()
        assert my_model.name == "Hans"
        assert len(Notes.objects.all()) == 1, "Should be no new objects"


