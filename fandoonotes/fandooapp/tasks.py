from __future__ import absolute_import
from self import self
from .models import Notes
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from .mailer import Mailer
""" The @shared_task decorator returns a proxy that always uses the task in the current app: """

mail = Mailer()
mail.send_messages(subject='FundooNote account verification',
                   template='fandooapp/mail.html',
                   context={'customer': self},
                   to_emails=['nilammore820@gmail.com'])


@shared_task
def count_notes():  # count the number of notes
    return Notes.objects.count()


@shared_task
def update_notes(note_id, title, trash, is_deleted):  # rename the title
    note = Notes.objects.get(id=note_id)
    note.title = title  # take title field
    note.trash = trash
    note.is_deleted = is_deleted
    note.save()
    return note

# to delete the notes of after every 10 days
@periodic_task(run_every=(crontab(0, 0, day_of_month='*/10')), name="delete_note", ignore_result=True)
def delete_notes(note_id):
    note = Notes.objects.get(id=note_id)
    note.delete()




