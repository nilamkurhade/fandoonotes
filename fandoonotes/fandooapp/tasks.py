from __future__ import absolute_import
import time
from .models import Notes
from itertools import chain
from celery import app
from celery import shared_task


""" The @shared_task decorator returns a proxy that always uses the task in the current app: """


@shared_task
@shared_task
def count_notes():  # count the number of notes
    return Notes.objects.count()


@shared_task
def update_notes(notes_id, title,trash, deleted):  # rename the title
    note = Notes.objects.get(id=notes_id)
    note.title = title  # take title field
    note.trash = trash
    note.deleted = deleted
    note.save()
    return note


@app.task
def longtime_add(x, y):
    print('long time task begins')
    # sleep 5 seconds
    time.sleep(5)
    print('long time task finished')
    return x + y
