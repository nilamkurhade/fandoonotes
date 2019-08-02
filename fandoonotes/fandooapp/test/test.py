from .views import LabelList
from .views import NotesList
from .views import NoteTrash
from .views import NoteArchiveview


def test_note_details(rf):
    request = rf.get('/Notes/')
    response = NotesList(request)
    assert response.status_code == 200


def test_labels_details(rf):
    request = rf.get('/labels/')
    response = LabelList(request)
    assert response.status_code == 200


def test_trash_details(rf):
    request = rf.get('/trash/')
    response = NoteTrash(request)
    assert response.status_code == 200


def test_archive_details(rf):
    request = rf.get('/archive/')
    response = NoteArchiveview(request)
    assert response.status_code == 200
