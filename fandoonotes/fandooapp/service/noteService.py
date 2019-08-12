from rest_framework import request
from .serializer import NoteSerializer
from .models import Notes
from .service import RedisServices
from django.contrib.auth.models import User
import jwt


class NoteServices:
    def __init__(self):
        pass

    def create_note(self):
        serializer = NoteSerializer(data=request.data)

    def get_notes(self):
        restoken = RedisServices.get_token(self, 'token')
        decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
        dec_id = decoded_token.get('id')
        user = User.objects.get(id=dec_id)
        notes = Notes.objects.filter(created_by=user, trash=False, is_deleted=False, is_archive=False)
        data = NoteSerializer(notes, many=True).data